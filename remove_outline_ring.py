import re

with open('turkey-wars/unit.gd', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Remove Ring code
ring_pattern = r'# Add visual colored ring.*?ring\.position\.y = 0\.05'
text = re.sub(ring_pattern, '', text, flags=re.DOTALL)

# 2. Remove outline apply code from _ready
outline_pattern = r'# Apply black outline.*?_apply_outline\(self, outline\)'
text = re.sub(outline_pattern, '', text, flags=re.DOTALL)

# 3. Replace _apply_outline with _apply_team_color
old_apply_func = r'func _apply_outline\(node: Node, mat: Material\):.*?_apply_outline\(child, mat\)'
new_apply_func = '''func _apply_team_color(node: Node, team_color: Color):
    if node is MeshInstance3D and node.mesh:
        for i in range(node.mesh.get_surface_count()):
            # Fallback to mesh material if override doesn't exist
            var mat = node.get_active_material(i)
            if mat and (mat is StandardMaterial3D or mat is ORMMaterial3D):
                var new_mat = mat.duplicate()
                # Multiply existing texture color with team color to tint it
                new_mat.albedo_color = new_mat.albedo_color * team_color
                node.set_surface_override_material(i, new_mat)
    
    for child in node.get_children():
        _apply_team_color(child, team_color)'''

text = re.sub(old_apply_func, new_apply_func, text, flags=re.DOTALL)

# 4. Inject team color call into _ready
ready_start = r'func _ready\(\):\n\s+add_to_group\("units"\)'
color_inj = '''func _ready():
    add_to_group("units")
    
    # Tint entire model to red or blue
    var tint = Color(1.0, 0.4, 0.4) if team == Team.ATTACKER else Color(0.4, 0.6, 1.0)
    _apply_team_color(self, tint)'''

text = re.sub(ready_start, color_inj, text)

with open('turkey-wars/unit.gd', 'w', encoding='utf-8') as f:
    f.write(text)

print("Swapped ring/outline for albedo tinting")
