import os

shader_code = '''shader_type spatial;
render_mode cull_front, unshaded;

uniform vec4 outline_color : source_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float outline_width = 0.015;

void vertex() {
    // Extrude the vertex along its normal
    vec3 normal = NORMAL;
    VERTEX += normal * outline_width;
}

void fragment() {
    ALBEDO = outline_color.rgb;
}
'''

with open('turkey-wars/outline.gdshader', 'w', encoding='utf-8') as f:
    f.write(shader_code)

mat_code = '''[gd_resource type="ShaderMaterial" load_steps=2 format=3 uid="uid://dx5outline1"]
[ext_resource type="Shader" path="res://outline.gdshader" id="1_out"]

[resource]
render_priority = 0
shader = ExtResource("1_out")
shader_parameter/outline_color = Color(0, 0, 0, 1)
shader_parameter/outline_width = 0.015
'''

with open('turkey-wars/outline_mat.tres', 'w', encoding='utf-8') as f:
    f.write(mat_code)

with open('turkey-wars/unit.gd', 'r', encoding='utf-8') as f:
    ug = f.read()

apply_func = '''func _apply_outline(node: Node, mat: Material):
    if node is MeshInstance3D:
        node.material_overlay = mat
    for child in node.get_children():
        _apply_outline(child, mat)

func _find_anim'''

if 'func _apply_outline' not in ug:
    ug = ug.replace('func _find_anim', apply_func)

ready_inj = '''
    # Apply black outline
    var outline = load("res://outline_mat.tres")
    if outline:
        _apply_outline(self, outline)
        
    if anim:'''

if '# Apply black outline' not in ug:
    ug = ug.replace('if anim:', ready_inj)

with open('turkey-wars/unit.gd', 'w', encoding='utf-8') as f:
    f.write(ug)

print("Outline added!")
