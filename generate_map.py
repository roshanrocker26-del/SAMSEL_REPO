import urllib.request
import json
import math

url = 'https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States'
with urllib.request.urlopen(url) as response:
    data = json.loads(response.read().decode())

states_to_include = ['Andhra Pradesh', 'Telangana', 'Telengana', 'Tamil Nadu', 'Kerala', 'Karnataka']

polygons = []
min_x = math.inf
max_x = -math.inf
min_y = math.inf
max_y = -math.inf

for feature in data['features']:
    name = feature['properties']['NAME_1']
    if name in states_to_include:
        geom = feature['geometry']
        coords = geom['coordinates']
        type_ = geom['type']
        
        # GeoJSON: [[lon, lat], [lon, lat]]
        state_polys = []
        if type_ == 'Polygon' or type_ == 'MultiPolygon':
            if type_ == 'Polygon':
                poly = coords[0]
                state_polys.append((name, poly))
            else:
                for p in coords:
                    state_polys.append((name, p[0]))
        
        for st_name, poly in state_polys:
            proj_poly = []
            for lon, lat in poly:
                x = lon
                # Simple mercator approximation for India latitudes
                y = -math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
                y = y * 180 / math.pi
                proj_poly.append((x, y))
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
            if len(proj_poly) > 10:
                polygons.append((st_name, proj_poly))

width = 600
height = 700
padding = 40

w = width - 2*padding
h = height - 2*padding

bx = max_x - min_x
by = max_y - min_y

scale = min(w/bx, h/by) if by > 0 else 1

cx = (min_x + max_x) / 2
cy = (min_y + max_y) / 2

def transform(x, y):
    nx = (x - cx) * scale + width/2
    ny = (y - cy) * scale + height/2
    return round(nx, 1), round(ny, 1)

svg_paths = []
for name, poly in polygons:
    path_data = []
    for i, (x, y) in enumerate(poly):
        px, py = transform(x, y)
        if i == 0:
            path_data.append(f"M {px},{py}")
        else:
            path_data.append(f"L {px},{py}")
    path_data.append("Z")
    
    d_string = " ".join(path_data)
    svg_paths.append(f'<path data-state="{name}" d="{d_string}" class="state-path"/>')

svg_content = "\n".join(svg_paths)

with open('map_out.txt', 'w', encoding='utf-8') as f:
    f.write(svg_content)
    
print("Generated map_out.txt with", len(polygons), "polygons.")
