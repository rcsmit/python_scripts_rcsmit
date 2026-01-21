import requests
import svgwrite
import sys

# Amsterdam centrum
minx, miny, maxx, maxy = 4.8900, 52.3700, 4.9000, 52.3750
miny, minx, maxy, maxx = 4.8900, 52.3700, 5.000, 52.3750

bag_wfs = "https://service.pdok.nl/lv/bag/wfs/v2_0"

# ➋ bbox mét CRS
bbox_str = f"{minx},{miny},{maxx},{maxy},EPSG:4326"

def fetch_geojson(url, params, naam):
    print(f"\n📡 Ophalen {naam}...")
    try:
        r = requests.get(url, params=params, timeout=30)
        print("URL:", r.url)  # handig voor debug
        r.raise_for_status()
        ct = r.headers.get("Content-Type","")
        if "json" not in ct.lower():
            print("⚠️ Geen JSON:", ct)
            print(r.text[:500])
            return None
        data = r.json()
        print("✅ features:", len(data.get("features", [])))
        return data
    except Exception as e:
        print("❌", e)
        return None

print("\n" + "="*60)
print("TEST 1: BAG PANDEN")
print("="*60)

params_pand = {
    "service": "WFS",
    "version": "2.0.0",
    "request": "GetFeature",
    # ➊ typenames i.p.v. typeName
    "typenames": "bag:pand",
    # ➌ echte GeoJSON
    "outputFormat": "application/json; subtype=geojson",
    "bbox": bbox_str,
    "srsName": "EPSG:4326",
    "count": "500000"
}

panden = fetch_geojson(bag_wfs, params_pand, "panden")

if not panden or len(panden.get("features", [])) == 0:
    print("\n❌ GEEN PANDEN GEVONDEN")
    print("Check: typenames, bbox met CRS, outputFormat")
    sys.exit(1)

# ---- SVG zoals jij had ----
width = maxx - minx
height = maxy - miny
svg_width = 1200
svg_height = int(svg_width * height / width)

def transform_coords(x, y):
    svg_x = ((x - minx) / width) * svg_width
    svg_y = ((maxy - y) / height) * svg_height
    return svg_x, svg_y

def process_geometry(geom):
    if geom["type"] == "Polygon":
        return [geom["coordinates"][0]]
    if geom["type"] == "MultiPolygon":
        return [poly[0] for poly in geom["coordinates"]]
    return []

dwg = svgwrite.Drawing("bag_panden.svg", size=(svg_width, svg_height))
dwg.viewbox(0, 0, svg_width, svg_height)
dwg.add(dwg.rect((0, 0), (svg_width, svg_height), fill="#f8f8f8"))

drawn = 0
for f in panden.get("features", []):
    geom = f.get("geometry")
    if not geom:
        continue
    for ring in process_geometry(geom):
        if len(ring) < 3:
            continue
        points = [transform_coords(x, y) for x, y in ring]
        dwg.add(dwg.polygon(points=points, fill="#ffffff", stroke="#333333", stroke_width=1))
        drawn += 1

dwg.save()
print(f"\n✅ SVG opgeslagen: bag_panden.svg")
print(f"   {drawn} polygonen getekend")
