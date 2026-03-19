import re

# 1. grass_scatter.gd - Grass density and height
with open('turkey-wars/grass_scatter.gd', 'r', encoding='utf-8') as f:
    gs = f.read()

gs = re.sub(r'grass_count:\ int\ =\ \d+', 'grass_count: int = 12000', gs) # Density++
gs = gs.replace('if multimesh == null or multimesh.instance_count == 0:\n\t\tgenerate_grass()', '\tgenerate_grass()') # Always auto-refresh
gs = re.sub(r'rng\.randf_range\(0\.6,\ 1\.2\)', 'rng.randf_range(0.12, 0.35)', gs) # Height-- (Massive decrease)

with open('turkey-wars/grass_scatter.gd', 'w', encoding='utf-8') as f:
    f.write(gs)

# 2. grass_simple_mat.tres - Grass opacity and saturation
with open('turkey-wars/grass_simple_mat.tres', 'r', encoding='utf-8') as f:
    gm = f.read()

gm = re.sub(r'albedo_top\ =\ Color\(.*?\)', 'albedo_top = Color(0.65, 0.75, 0.5, 1)', gm)
gm = re.sub(r'albedo_bottom\ =\ Color\(.*?\)', 'albedo_bottom = Color(0.35, 0.45, 0.3, 1)', gm)
gm = re.sub(r'opacity\ =\ [\d\.]+', 'opacity = 0.15', gm)

with open('turkey-wars/grass_simple_mat.tres', 'w', encoding='utf-8') as f:
    f.write(gm)

# 3. battlefield.tscn - Plane saturation
with open('turkey-wars/battlefield.tscn', 'r', encoding='utf-8') as f:
    bt = f.read()

bt = re.sub(r'albedo_color\ =\ Color\(.*?\)', 'albedo_color = Color(0.65, 0.65, 0.65, 1)', bt)

with open('turkey-wars/battlefield.tscn', 'w', encoding='utf-8') as f:
    f.write(bt)

# 4. unit.gd - Color coding troops
with open('turkey-wars/unit.gd', 'r', encoding='utf-8') as f:
    ug = f.read()

ring_code = '''
    # Add visual colored ring
    var ring = MeshInstance3D.new()
    var torus = TorusMesh.new()
    torus.inner_radius = 0.5
    torus.outer_radius = 0.6
    ring.mesh = torus
    var mat = StandardMaterial3D.new()
    
    # Red for attacker, Blue for defender
    mat.albedo_color = Color(1.0, 0.1, 0.1) if team == Team.ATTACKER else Color(0.1, 0.4, 1.0)
    mat.emission_enabled = true
    mat.emission = mat.albedo_color
    mat.emission_energy = 2.0
    mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
    mat.albedo_color.a = 0.8
    ring.material_override = mat
    add_child(ring)
    ring.position.y = 0.05
    
    # Auto-detect animation names by keyword (foolproof for different asset packs)'''

ug = ug.replace('# Auto-detect animation names by keyword (foolproof for different asset packs)', ring_code)

with open('turkey-wars/unit.gd', 'w', encoding='utf-8') as f:
    f.write(ug)

# 5. ranger.tscn - Ranger range
with open('turkey-wars/ranger.tscn', 'r', encoding='utf-8') as f:
    rt = f.read()

rt = re.sub(r'attack_range\ =\ 15\.0', 'attack_range = 35.0', rt)

with open('turkey-wars/ranger.tscn', 'w', encoding='utf-8') as f:
    f.write(rt)

print("Tweaks applied successfully.")
