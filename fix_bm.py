with open('turkey-wars/battle_manager.gd', 'r', encoding='utf-8') as f:
    text = f.read()

import re

# Add ranger scene export
text = text.replace('@export var warrior_scene: PackedScene', '@export var warrior_scene: PackedScene\n@export var ranger_scene: PackedScene')

# Add ranger default
text = text.replace('warrior_scene = load("res://warrior.tscn")', 'warrior_scene = load("res://warrior.tscn")\n    if not ranger_scene:\n        ranger_scene = load("res://ranger.tscn")')

# Replace _ready completely to make code cleaner
ready_pattern = r'# Spawn 3 Attacker Warriors \(Left Team\)(.*?)# Optional: Slightly color'
replacement = '''# Spawn Attackers (Left Team)
    spawn_unit(0, false, warrior_scene) # Frontline
    spawn_unit(0, false, warrior_scene) # Frontline
    spawn_unit(0, false, warrior_scene) # Frontline
    spawn_unit(0, true, ranger_scene)   # Backline
    spawn_unit(0, true, ranger_scene)   # Backline
    
    # Spawn Defenders (Right Team)
    spawn_unit(1, false, warrior_scene) # Frontline
    spawn_unit(1, false, warrior_scene) # Frontline
    spawn_unit(1, false, warrior_scene) # Frontline
    spawn_unit(1, true, ranger_scene)   # Backline
    spawn_unit(1, true, ranger_scene)   # Backline

func spawn_unit(team: int, is_backline: bool, scene_to_spawn: PackedScene):
    var spawn_area: CSGBox3D = null
    if team == 0:
        spawn_area = attacker_back if is_backline else attacker_front
    else:
        spawn_area = defender_back if is_backline else defender_front
        
    var unit = scene_to_spawn.instantiate()
    unit.team = team
    unit.is_backline = is_backline
    add_child(unit)
    
    # Calculate random point inside the chosen visual box area
    # CSGBox3D's scale dictates its physical dimensions from -0.5 to 0.5 in local space.
    var sx = spawn_area.scale.x
    var sz = spawn_area.scale.z
    
    var rx = randf_range(-0.5, 0.5) * sx
    var rz = randf_range(-0.5, 0.5) * sz
    
    # Place unit precisely inside the target box area safely onto the ground
    unit.global_position = spawn_area.global_position + Vector3(rx, 0, rz)
    
    # Optional: Slightly color'''

text = re.sub(ready_pattern, replacement, text, flags=re.DOTALL)

with open('turkey-wars/battle_manager.gd', 'w', encoding='utf-8') as f:
    f.write(text)

print("bm fixed")
