extends Node

# Global game state manager to pass data between the Map and the Battlefield

var players = [
	{"name": "Mark", "color": Color(0.8, 0.2, 0.2), "army": 35000, "alive": true},
	{"name": "James", "color": Color(0.2, 0.8, 0.2), "army": 35000, "alive": true},
	{"name": "Avery", "color": Color(0.2, 0.2, 0.8), "army": 35000, "alive": true}
]

var neutral_cities = {} # province_name -> army_size
var province_owners = {} # province_name -> player_index
var capitals = {} # player_index -> province_name

var current_turn = 0
var game_phase = "picking" # "picking", "playing"

var attack_data = {
	"attacker_idx": -1,
	"defender_idx": -1, # -1 if neutral
	"province": "",
	"attacker_army": {"warrior": 0, "ranger": 0, "wizard": 0, "rocket_launcher": 0},
	"defender_army": {"warrior": 0, "ranger": 0, "wizard": 0, "rocket_launcher": 0},
	"is_capital": false,
	"neutral_size": 0
}

const UNIT_COSTS = {
	"warrior": 350,
	"ranger": 700,
	"wizard": 2500,
	"rocket_launcher": 2500
}

var last_save_path = "user://saves/default.json"

func start_battle(attacker, defender, prov):
	attack_data.attacker_idx = attacker
	attack_data.defender_idx = defender
	attack_data.province = prov
	
	if defender == -1:
		attack_data.neutral_size = neutral_cities.get(prov, 10000)
		attack_data.is_capital = false
	else:
		attack_data.is_capital = (capitals.get(defender) == prov)
	
	# Transition to troop selection UI or battlefield
	get_tree().change_scene_to_file("res://troop_selector.tscn")

func resolve_battle(attacker_won: bool):
	var prov = attack_data.province
	var def_idx = attack_data.defender_idx
	var att_idx = attack_data.attacker_idx
	
	var city_value = 0
	if def_idx == -1:
		city_value = attack_data.neutral_size
	elif not attack_data.is_capital:
		# For now, base it on a fixed amount
		city_value = 10000 
		
	var bonus = city_value / 10
	
	if attacker_won:
		province_owners[prov] = att_idx
		players[att_idx].army += bonus
		
		# If we defeated another player
		if def_idx != -1:
			if not attack_data.is_capital:
				players[def_idx].army -= bonus
			else:
				# Capital taken! Eliminate the player.
				players[def_idx]["alive"] = false
				print(players[def_idx]["name"] + " is eliminated!")
				
				# All their other cities turn neutral
				var provinces_to_clear = []
				for p_name in province_owners:
					if province_owners[p_name] == def_idx and p_name != prov:
						provinces_to_clear.append(p_name)
				
				for p_name in provinces_to_clear:
					province_owners.erase(p_name)
	
	# Reset and go back to map
	next_turn()
	get_tree().change_scene_to_file("res://map_scene.tscn")

func next_turn():
	# Ensure we don't get stuck if somehow no one is alive
	var alive_count = 0
	for p in players:
		if p.get("alive", true):
			alive_count += 1
	
	if alive_count <= 1:
		# Game over logic could go here, but for now just advance
		current_turn = (current_turn + 1) % players.size()
		return

	current_turn = (current_turn + 1) % players.size()
	while not players[current_turn].get("alive", true):
		current_turn = (current_turn + 1) % players.size()
