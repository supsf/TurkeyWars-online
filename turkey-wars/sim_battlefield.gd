extends Node

const TIME_STEP: float = 0.1
const BUDGET: float = 50000.0
const MAX_TICKS: int = 5000 # Safety timeout
const SAVE_PATH: String = "user://balance_sim_results.json"

var melee_cost: float = 280.0
var ranged_cost: float = 550.0
var tank_cost: float = 2000.0
var rocket_cost: float = 1700.0

var battles_run: int = 0
var results: Array = []
var is_simulating: bool = true

# Updated stats as per request
var stats = {
	"melee": {
		"hp": 125.0,
		"damage": 50.0, 
		"rate": 1.0 / 1.43,
		"range": 2.0,
		"speed": 4.5
	},
	"ranged": {
		"hp": 200.0,
		"damage": 35.0,
		"rate": 1.0 / 1.43,
		"range": 25.0,
		"speed": 3.0
	},
	"tank": {
		"hp": 1500.0,
		"damage": 300.0,
		"rate": 1.0 / 0.5,
		"range": 7.0,
		"speed": 6.0
	},
	"rocket": {
		"hp": 300.0,
		"damage": 50.0,
		"rate": 1.0 / 0.33,
		"range": 50.0,
		"speed": 3.0,
		"aoe_radius": 4.0,
		"aoe_damage": 25.0
	}
}

class SimUnit:
	var type: String
	var team: int
	var hp: float
	var max_hp: float
	var damage: float
	var rate: float
	var range: float
	var speed: float
	var aoe_radius: float = 0.0
	var aoe_damage: float = 0.0
	
	var pos: Vector2
	var attack_timer: float = 0.0
	var target: SimUnit = null

	func _init(t: String, tm: int, st: Dictionary, p: Vector2):
		type = t
		team = tm
		max_hp = st["hp"]
		hp = max_hp
		damage = st["damage"]
		rate = st["rate"]
		range = st["range"]
		speed = st["speed"]
		if st.has("aoe_radius"):
			aoe_radius = st["aoe_radius"]
			aoe_damage = st["aoe_damage"]
		pos = p
		attack_timer = randf() * rate

func _ready() -> void:
	print("--- Headless Balance Simulation (Rocket Launchers Included) Started ---")
	print("Press F6 to restart. Saving to: ", ProjectSettings.globalize_path(SAVE_PATH))
	randomize()
	_save_results()

func _process(_delta: float) -> void:
	if not is_simulating: return
	for _i in range(10):
		_run_battle()

func _draft_army() -> Dictionary:
	var army = {"melee": 0, "ranged": 0, "tank": 0, "rocket": 0}
	var current = BUDGET
	
	while true:
		var inv_melee = 1.0 / melee_cost
		var inv_ranged = 1.0 / ranged_cost
		var inv_tank = 1.0 / tank_cost
		var inv_rocket = 1.0 / rocket_cost
		var total_weight = inv_melee + inv_ranged + inv_tank + inv_rocket
		
		var roll = randf() * total_weight
		var choice = ""
		
		if roll < inv_melee: choice = "melee"
		elif roll < inv_melee + inv_ranged: choice = "ranged"
		elif roll < inv_melee + inv_ranged + inv_tank: choice = "tank"
		else: choice = "rocket"
		
		var cost = 0.0
		if choice == "melee": cost = melee_cost
		elif choice == "ranged": cost = ranged_cost
		elif choice == "tank": cost = tank_cost
		else: cost = rocket_cost
		
		if current >= cost:
			army[choice] += 1
			current -= cost
		else:
			# Fallback to cheapest or break
			if current >= melee_cost:
				army["melee"] += 1
				current -= melee_cost
			else:
				break
	return army

func _run_battle() -> void:
	var team0_comp = _draft_army()
	var team1_comp = _draft_army()
	
	var units: Array[SimUnit] = []
	_spawn_team(units, 0, team0_comp, -30)
	_spawn_team(units, 1, team1_comp, 30)
		
	var ticks = 0
	while ticks < MAX_TICKS:
		var team0_alive = false
		var team1_alive = false
		
		# 1. Update targeting
		for u in units:
			if u.hp <= 0: continue
			if u.team == 0: team0_alive = true
			else: team1_alive = true
			
			if u.target == null or u.target.hp <= 0:
				u.target = _find_best_target(u, units)
		
		if not team0_alive or not team1_alive: break
			
		# 2. Update combat
		for u in units:
			if u.hp <= 0 or u.target == null: continue
			var dist = u.pos.distance_to(u.target.pos)
			if dist <= u.range:
				u.attack_timer -= TIME_STEP
				if u.attack_timer <= 0:
					_execute_attack(u, units)
					u.attack_timer = u.rate
			else:
				var dir = (u.target.pos - u.pos).normalized()
				u.pos += dir * u.speed * TIME_STEP
		ticks += 1
		
	_determine_and_record_winner(team0_comp, team1_comp, units)

func _find_best_target(u: SimUnit, all_units: Array) -> SimUnit:
	var best_dist = 999999.0
	var best_target: SimUnit = null
	
	# Rocket Priority logic: target "ranged" (riflemen) units first
	var prioritize_ranged = (u.type == "rocket")
	var ranged_enemies = []
	if prioritize_ranged:
		for e in all_units:
			if e.hp > 0 and e.team != u.team and e.type == "ranged":
				ranged_enemies.append(e)
	
	# If rocket and there are ranged enemies, only look at them
	var targets_to_search = ranged_enemies if not ranged_enemies.is_empty() else all_units
	
	for e in targets_to_search:
		if e.hp > 0 and e.team != u.team:
			var d = u.pos.distance_squared_to(e.pos)
			if d < best_dist:
				best_dist = d
				best_target = e
	return best_target

func _execute_attack(u: SimUnit, all_units: Array):
	u.target.hp -= u.damage
	
	# AOE Splash
	if u.aoe_radius > 0:
		var impact_pos = u.target.pos
		for e in all_units:
			if e.hp > 0 and e.team != u.team and e != u.target:
				if e.pos.distance_to(impact_pos) <= u.aoe_radius:
					e.hp -= u.aoe_damage

func _determine_and_record_winner(t0_comp, t1_comp, units):
	var t0_hp = 0.0
	var t1_hp = 0.0
	for u in units:
		if u.hp > 0:
			if u.team == 0: t0_hp += u.hp
			else: t1_hp += u.hp
			
	var winner = -1
	if t0_hp > 0 and t1_hp <= 0: winner = 0
	elif t1_hp > 0 and t0_hp <= 0: winner = 1
	
	_adjust_costs(winner, t0_comp, t1_comp)

func _spawn_team(units: Array, team_idx: int, comp: Dictionary, offset: float):
	for i in range(comp["melee"]):
		units.append(SimUnit.new("melee", team_idx, stats["melee"], Vector2(offset + randf_range(-5, 5), randf_range(-15, 15))))
	for i in range(comp["ranged"]):
		units.append(SimUnit.new("ranged", team_idx, stats["ranged"], Vector2(offset * 1.5 + randf_range(-5, 5), randf_range(-15, 15))))
	for i in range(comp["tank"]):
		units.append(SimUnit.new("tank", team_idx, stats["tank"], Vector2(offset * 2.0 + randf_range(-5, 5), randf_range(-15, 15))))
	for i in range(comp["rocket"]):
		units.append(SimUnit.new("rocket", team_idx, stats["rocket"], Vector2(offset * 2.5 + randf_range(-5, 5), randf_range(-15, 15))))

func _adjust_costs(winner: int, t0: Dictionary, t1: Dictionary) -> void:
	if winner == -1: return
	
	var win_comp = t0 if winner == 0 else t1
	var lose_comp = t1 if winner == 0 else t0
	
	var win_total = float(win_comp["melee"] + win_comp["ranged"] + win_comp["tank"] + win_comp["rocket"])
	var lose_total = float(lose_comp["melee"] + lose_comp["ranged"] + lose_comp["tank"] + lose_comp["rocket"])
	
	if win_total == 0 or lose_total == 0: return
	
	var r_diff = (float(win_comp["ranged"]) / win_total) - (float(lose_comp["ranged"]) / lose_total)
	var m_diff = (float(win_comp["melee"]) / win_total) - (float(lose_comp["melee"]) / lose_total)
	var t_diff = (float(win_comp["tank"]) / win_total) - (float(lose_comp["tank"]) / lose_total)
	var rk_diff = (float(win_comp["rocket"]) / win_total) - (float(lose_comp["rocket"]) / lose_total)
	
	var adj = 20.0
	ranged_cost += r_diff * adj
	melee_cost += m_diff * adj
	tank_cost += t_diff * adj * 5.0
	rocket_cost += rk_diff * adj * 3.0
	
	ranged_cost = clamp(ranged_cost, 50.0, 5000.0)
	melee_cost = clamp(melee_cost, 50.0, 5000.0)
	tank_cost = clamp(tank_cost, 500.0, 10000.0)
	rocket_cost = clamp(rocket_cost, 200.0, 8000.0)
	
	battles_run += 1
	results.append({
		"battle_id": battles_run,
		"costs": {"m": int(melee_cost), "r": int(ranged_cost), "t": int(tank_cost), "rk": int(rocket_cost)}
	})
	
	if battles_run % 20 == 0:
		print("B: %d | M: %d | R: %d | T: %d | RK: %d" % [battles_run, int(melee_cost), int(ranged_cost), int(tank_cost), int(rocket_cost)])
		_save_results()

func _save_results() -> void:
	var file = FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file:
		file.store_string(JSON.stringify(results, "\t"))
		file.close()
