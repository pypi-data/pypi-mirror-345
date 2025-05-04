import os
import re
import datetime
import requests

CATALOG_SEARCH_URL = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"

def convert_polygon_wkt_to_array(wkt_string):
    coords_text = re.search(r'POLYGON\(\((.*?)\)\)', wkt_string).group(1)
    coords = [tuple(map(float, coord.strip().split())) for coord in coords_text.split(',')]
    if coords[0] != coords[-1]:
        coords.append(coords[0])
    return [coords]

def get_bbox(polygon_coords):
    lons, lats = zip(*polygon_coords[0])
    return [min(lons), min(lats), max(lons), max(lats)]

def ensure_output_dir(base_path, date_str, vis_type):
    path = os.path.join(base_path, date_str, vis_type)
    os.makedirs(path, exist_ok=True)
    return path

def find_best_date(token, bbox, target_date, days_range, max_cloud, platform):
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    dates = [(datetime.datetime.fromisoformat(target_date) + datetime.timedelta(days=i)).date().isoformat()
             for i in range(-days_range, days_range+1)]
    collection = "sentinel-2-l2a" if platform == "sentinel-2" else "sentinel-1-grd"

    best = None
    min_delta = float('inf')

    for d in dates:
        payload = {
            "bbox": bbox,
            "datetime": f"{d}T00:00:00.000Z/{d}T23:59:59.999Z",
            "collections": [collection],
            "limit": 10
        }
        if platform == "sentinel-2":
            payload["filter"] = {
                "op": "<=",
                "args": [{"property": "eo:cloud_cover"}, max_cloud]
            }
            payload["filter-lang"] = "cql2-json"

        r = requests.post(CATALOG_SEARCH_URL, headers=headers, json=payload)
        if r.status_code == 200 and r.json().get("features"):
            delta = abs((datetime.datetime.fromisoformat(d) - datetime.datetime.fromisoformat(target_date)).days)
            if delta < min_delta:
                best = d
                min_delta = delta

    return best