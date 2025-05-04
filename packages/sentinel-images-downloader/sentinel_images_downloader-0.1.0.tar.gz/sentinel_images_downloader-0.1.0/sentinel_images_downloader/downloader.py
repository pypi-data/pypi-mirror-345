import os
import requests
from io import BytesIO
from .auth import get_access_token
from .utils import (
    convert_polygon_wkt_to_array,
    find_best_date,
    ensure_output_dir,
    get_bbox
)
from .evalscripts import EVALSCRIPTS, get_band_evalscript_s2, get_band_evalscript_s1

API_URL = "https://sh.dataspace.copernicus.eu/api/v1/process"
CATALOG_SEARCH_URL = "https://sh.dataspace.copernicus.eu/api/v1/catalog/1.0.0/search"

def download_sentinel_image(client_id, client_secret, polygon_wkt, target_date,
                             days_range, max_cloud_cover=100, visualization="true_color",
                             save_dir=None, platform="sentinel-2", band=None, resolution=512):
    token = get_access_token(client_id, client_secret)
    polygon_coords = convert_polygon_wkt_to_array(polygon_wkt)
    bbox = get_bbox(polygon_coords)

    best_date = find_best_date(token, bbox, target_date, days_range, max_cloud_cover, platform)
    if not best_date:
        raise ValueError("No suitable image found in given date range.")

    headers = {"Authorization": f"Bearer {token}"}

    if platform == "sentinel-2":
        if band:
            evalscript = get_band_evalscript_s2(band)
            data_type = "S2L2A"
            name = band
        else:
            evalscript = EVALSCRIPTS.get(visualization)
            data_type = "S2L2A"
            name = visualization
    elif platform == "sentinel-1":
        if band:
            evalscript = get_band_evalscript_s1(band)
            name = band
        else:
            evalscript = EVALSCRIPTS.get(visualization)
            name = visualization
        data_type = "S1GRD"
    else:
        raise ValueError("Platform must be 'sentinel-1' or 'sentinel-2'")

    if not evalscript:
        raise ValueError(f"Unknown visualization type or band: {visualization or band}")

    request_payload = {
        "input": {
            "bounds": {"geometry": {"type": "Polygon", "coordinates": polygon_coords}},
            "data": [{
                "type": data_type,
                "dataFilter": {
                    "timeRange": {
                        "from": f"{best_date}T00:00:00Z",
                        "to": f"{best_date}T23:59:59Z"
                    }
                }
            }]
        },
        "evalscript": evalscript,
        "output": {
            "width": resolution,
            "height": resolution,
            "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}]
        }
    }

    response = requests.post(API_URL, headers=headers, json=request_payload)
    if response.status_code == 200:
        if save_dir:
            output_dir = ensure_output_dir(save_dir, best_date, name)
            output_path = os.path.join(output_dir, f"{name}.tiff")
            with open(output_path, "wb") as f:
                f.write(response.content)
            return output_path, best_date
        else:
            return BytesIO(response.content), best_date
    else:
        raise RuntimeError(f"Failed to download image: {response.status_code} {response.text}")