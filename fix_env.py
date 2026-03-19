import re

with open('turkey-wars/battlefield.tscn', 'r', encoding='utf-8') as f:
    text = f.read()

# the procedural sky section
sky_pattern = r'\[sub_resource type=.ProceduralSkyMaterial.*?\](.*?)\[sub_resource type=.Sky.*?\]'
replacement_sky = '''[sub_resource type="ProceduralSkyMaterial" id="ProceduralSkyMaterial_sky"]
sky_top_color = Color(0.3, 0.45, 0.7, 1)
sky_horizon_color = Color(0.7, 0.8, 0.9, 1)
sky_curve = 0.05
ground_bottom_color = Color(0.1, 0.15, 0.05, 1)
ground_horizon_color = Color(0.7, 0.8, 0.9, 1)
ground_curve = 0.05

[sub_resource type="Sky" id="Sky_afternoon"]'''
text = re.sub(sky_pattern, replacement_sky, text, flags=re.DOTALL)

# the environment section
env_pattern = r'\[sub_resource type=.Environment. id=.Environment_afternoon.*?\](.*?)\[node'
replacement_env = '''[sub_resource type="Environment" id="Environment_afternoon"]
background_mode = 2
sky = SubResource("Sky_afternoon")
tonemap_mode = 2
tonemap_exposure = 1.05
tonemap_white = 1.1
glow_enabled = true
glow_bloom = 0.05
volumetric_fog_enabled = true
volumetric_fog_density = 0.002
volumetric_fog_albedo = Color(0.9, 0.92, 0.95, 1)

[node'''
text = re.sub(env_pattern, replacement_env, text, flags=re.DOTALL)

with open('turkey-wars/battlefield.tscn', 'w', encoding='utf-8') as f:
    f.write(text)

print('Done')
