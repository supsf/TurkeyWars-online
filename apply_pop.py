import re

with open('turkey-wars/unit.gd', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Upgrade the _apply_team_color function with Rim Lighting and Emission
old_apply = r'func _apply_team_color\(node: Node, team_color: Color\):.*?func _ready\(\):'
new_apply = '''func _apply_team_color(node: Node, team_color: Color):
    if node is MeshInstance3D and node.mesh:
        for i in range(node.mesh.get_surface_count()):
            # Fallback to mesh material if override doesn't exist
            var mat = node.get_active_material(i)
            if mat and (mat is StandardMaterial3D or mat is ORMMaterial3D):
                var new_mat = mat.duplicate()
                
                # 1. Vibrant Color Interpolation (leaves dark fold details but severely tints highlights)
                new_mat.albedo_color = Color(1, 1, 1).lerp(team_color, 0.7)
                
                # 2. Rim Lighting (Holy Grail from Gemini's suggestions)
                if new_mat is StandardMaterial3D:
                    new_mat.rim_enabled = true
                    new_mat.rim = 1.0
                    new_mat.rim_tint = 1.0
                
                # 3. Soft Self-Illumination (Makes them pop in shadowed areas)
                new_mat.emission_enabled = true
                new_mat.emission = team_color
                new_mat.emission_energy_multiplier = 0.4
                
                node.set_surface_override_material(i, new_mat)
    
    for child in node.get_children():
        _apply_team_color(child, team_color)

func _ready():'''

text = re.sub(old_apply, new_apply, text, flags=re.DOTALL)

# 2. Update the team colors in _ready to be highly saturated, and slightly increase unit size for silhouette emphasis
color_inj = r'var tint = Color.*?_apply_team_color\(self, tint\)'
new_color_inj = '''# Emphasize Silhouette by scaling up units slightly
    scale = Vector3(1.2, 1.2, 1.2)
    
    # Highly saturated neon team colors
    var tint = Color(1.0, 0.05, 0.05) if team == Team.ATTACKER else Color(0.05, 0.3, 1.0)
    _apply_team_color(self, tint)'''

text = re.sub(color_inj, new_color_inj, text, flags=re.DOTALL)

with open('turkey-wars/unit.gd', 'w', encoding='utf-8') as f:
    f.write(text)

print("Pop tweaks applied successfully!")
