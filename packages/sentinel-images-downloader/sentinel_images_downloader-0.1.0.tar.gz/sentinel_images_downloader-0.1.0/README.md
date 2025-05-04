# Sentinel Images Downloader

A Python library for downloading Sentinel-1 and Sentinel-2 satellite images from the Copernicus Data Space Ecosystem.

---

## 🚀 Features
- ✅ Supports Sentinel-1 and Sentinel-2 satellites
- ☁️ Cloud coverage filtering (for Sentinel-2)
- 📅 Flexible date range (±N days from target)
- 🗺️ Input via WKT polygon format
- 🎯 Download individual bands or prebuilt visualizations
- 📦 TIFF output with geospatial metadata
- ⚙️ Resolution control (default: 512×512)
- 🧠 In-memory or file output

---

## 📦 Installation
```bash
pip install sentinel_images_downloader
```

---

## 🔐 How to Get CLIENT_ID and CLIENT_SECRET
1. Go to [Copernicus Data Space Ecosystem](https://dataspace.copernicus.eu/)
2. Create an account or log in
3. Go to **My Profile → API Keys**
4. Click **Create API Key**
5. Save your **Client ID** and **Client Secret**

---

## Basic Usage
```python
from sentinel_images_downloader import download_sentinel_image

polygon = "POLYGON((30.0 50.0, 30.1 50.0, 30.1 50.1, 30.0 50.1, 30.0 50.0))"

img_data, date = download_sentinel_image(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    polygon_wkt=polygon,
    target_date="2024-05-10",
    days_range=3,                  # +/- N days from target_date
    max_cloud_cover=20,            # Applied only for Sentinel-2 
    visualization="true_color",   # Options: 'true_color', 'false_color', 'ndvi', 'ndwi', etc.
    platform="sentinel-2",        # Options: 'sentinel-1' or 'sentinel-2'
    save_dir="results",           # Optional. If omitted, image is returned in memory (BytesIO)
    resolution=1024                # Optional. Default is 512 Max: 2500 (API dependent)
)

print(f"Image saved to {img_data} from date {date}")
```

---

## Download a Specific Band
```python
img_data, date = download_sentinel_image(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    polygon_wkt=polygon,
    target_date="2024-05-10",
    days_range=3,
    max_cloud_cover=10,
    band="B08",                   # Sentinel-2 band (e.g., B01..B12)
    platform="sentinel-2",
    resolution=512
)
```

---

## Download from Sentinel-1
```python
img_data, date = download_sentinel_image(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    polygon_wkt=polygon,
    target_date="2024-05-10",
    days_range=5,
    visualization="rvi",         # Options: 'rvi', or use band="VV" / "VH"
    platform="sentinel-1"
)
```

---

## Output Structure
If `save_dir` is used, files are saved as:
```
{save_dir}/YYYY-MM-DD/{visualization_or_band}/{name}.tiff
```

If `save_dir` is omitted, function returns `BytesIO`, suitable for:
```python
import rasterio
with rasterio.open(img_data) as src:
    image = src.read(1)  # or [1, 2, 3] if RGB
```

---

## ⚠️ Notes
- Sentinel-1 ignores cloud cover value
- Default resolution is 512×512 (can be changed via `resolution`)
- Default max_cloud_cover is 100
- Images returned as TIFFs (georeferenced)
- For displaying in Jupyter use `rasterio` + `matplotlib`

---

## 📄 License
[MIT](./LICENSE.txt)