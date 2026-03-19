import re

# 1. grass_simple_mat.tres - Make grass brighter and less transparent
with open('turkey-wars/grass_simple_mat.tres', 'r', encoding='utf-8') as f:
    gm = f.read()

gm = re.sub(r'albedo_top = Color\(.*?\)', 'albedo_top = Color(0.85, 0.95, 0.4, 1)', gm)
gm = re.sub(r'albedo_bottom = Color\(.*?\)', 'albedo_bottom = Color(0.4, 0.65, 0.25, 1)', gm)
gm = re.sub(r'opacity = [\d\.]+', 'opacity = 0.5', gm)

with open('turkey-wars/grass_simple_mat.tres', 'w', encoding='utf-8') as f:
    f.write(gm)

# 2. battlefield.tscn - Restore plane brightness and enhance environment vibrance
with open('turkey-wars/battlefield.tscn', 'r', encoding='utf-8') as f:
    bt = f.read()

# Restore Plane Albedo
bt = re.sub(r'albedo_color = Color\(.*?\)', 'albedo_color = Color(1.0, 1.0, 1.0, 1)', bt)

# Enhance Sky/Ground to be much more vibrant
bt = re.sub(r'sky_top_color = Color\(.*?\)', 'sky_top_color = Color(0.15, 0.45, 0.85, 1)', bt)
bt = re.sub(r'sky_horizon_color = Color\(.*?\)', 'sky_horizon_color = Color(0.65, 0.85, 0.95, 1)', bt)
bt = re.sub(r'ground_bottom_color = Color\(.*?\)', 'ground_bottom_color = Color(0.1, 0.25, 0.1, 1)', bt)
bt = re.sub(r'ground_horizon_color = Color\(.*?\)', 'ground_horizon_color = Color(0.65, 0.85, 0.95, 1)', bt)

# Increase ACES exposure/tonemapping for global vibrance
bt = re.sub(r'tonemap_exposure = [\d\.]+', 'tonemap_exposure = 1.25', bt)
bt = re.sub(r'tonemap_white = [\d\.]+', 'tonemap_white = 1.0', bt)

# Enhance sun light energy to pop colors
bt = re.sub(r'light_energy = [\d\.]+', 'light_energy = 1.5', bt)

with open('turkey-wars/battlefield.tscn', 'w', encoding='utf-8') as f:
    f.write(bt)

print("Brightened scene successfully.")
