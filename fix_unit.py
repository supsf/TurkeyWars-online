import re

with open('turkey-wars/unit.gd', 'r', encoding='utf-8') as f:
    text = f.read()

# Add the export variable
header_pattern = r'(@export var is_backline: bool = false)'
text = re.sub(header_pattern, r'\1\n@export var projectile_scene: PackedScene', text)

# Add bow shoot to attack strings
attack_str_pattern = r'(anim_attack = _find_anim\("sword_attack"\))'
text = re.sub(attack_str_pattern, r'\1\n        if anim_attack == "": anim_attack = _find_anim("bow_shoot")', text)

# Replace perform_attack logic
attack_pattern = r'func _perform_attack\(\):.*?(?=func take_damage)'
replacement = '''func _perform_attack():
    # Attempt to deliver damage on the impact frame
    # We estimate the punch connects around 30% of the way into the attack speed
    var hit_delay = (1.0 / attack_speed) * 0.3
    if is_ranged: hit_delay = (1.0 / attack_speed) * 0.5 # Wait a bit longer to release arrow
    await get_tree().create_timer(hit_delay).timeout
    
    if current_state == State.DEAD or not target: return
    
    if is_ranged and projectile_scene:
        var proj = projectile_scene.instantiate()
        get_parent().add_child(proj)
        # Spawn arrow approximately at bow/chest height
        proj.global_position = global_position + Vector3(0, 1.2, 0)
        proj.fire(target, attack_damage)
    else:
        # Re-verify distance just in case target moved away
        var dist = global_position.distance_to(target.global_position)
        if dist <= attack_range * 1.5:
            target.take_damage(attack_damage)

'''
text = re.sub(attack_pattern, replacement, text, flags=re.DOTALL)

with open('turkey-wars/unit.gd', 'w', encoding='utf-8') as f:
    f.write(text)

print("unit.gd fixed")
