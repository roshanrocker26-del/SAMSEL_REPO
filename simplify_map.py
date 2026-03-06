import urllib.request
import json
import math

# Use a known simple GeoJSON for Indian States:
# Let's write a simplification function
def simplify(points, tolerance):
    if len(points) < 3: return points
    def point_line_distance(p, p1, p2):
        if p1[0] == p2[0] and p1[1] == p2[1]:
            return math.hypot(p[0]-p1[0], p[1]-p1[1])
        num = abs((p2[1]-p1[1])*p[0] - (p2[0]-p1[0])*p[1] + p2[0]*p1[1] - p2[1]*p1[0])
        den = math.hypot(p2[1]-p1[1], p2[0]-p1[0])
        return num / den

    dmax = 0
    index = 0
    for i in range(1, len(points)-1):
        d = point_line_distance(points[i], points[0], points[-1])
        if d > dmax:
            index = i
            dmax = d
            
    if dmax > tolerance:
        rec1 = simplify(points[:index+1], tolerance)
        rec2 = simplify(points[index:], tolerance)
        return rec1[:-1] + rec2
    else:
        return [points[0], points[-1]]

# Reload original huge data, simplify it!
import urllib.request
url_huge = 'https://raw.githubusercontent.com/Subhash9325/GeoJson-Data-of-Indian-States/master/Indian_States'
with urllib.request.urlopen(url_huge) as response:
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
                y = -math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
                y = y * 180 / math.pi
                proj_poly.append((x, y))
                
            # SIMPLIFY
            proj_poly = simplify(proj_poly, 0.05) # 0.05 degrees tolerance is roughly 5km
            
            if len(proj_poly) > 10:
                polygons.append((st_name, proj_poly))
                # Update bounds only after simplify
                for x, y in proj_poly:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)

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
    svg_paths.append(f'<path data-state="{name}" d="{d_string}" class="map-path" fill="none" stroke="url(#mapGradient)" stroke-width="4" stroke-linejoin="round" stroke-dasharray="3500" stroke-dashoffset="3500"/>')

svg_content = "\n".join(svg_paths)
with open('map_out.txt', 'w', encoding='utf-8') as f:
    f.write(svg_content)
