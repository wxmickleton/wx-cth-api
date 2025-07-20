import requests
import rasterio
import numpy as np
import tempfile

def get_cloud_top_height(lat, lon):
    bbox_size = 0.05
    width = 64
    height = 64

    south = lat - bbox_size
    north = lat + bbox_size
    west = lon - bbox_size
    east = lon + bbox_size

    wms_url = (
        "https://view.eumetsat.int/geoserver/ows?"
        f"service=WMS&request=GetMap&version=1.3.0"
        f"&layers=msg_fes:cth"
        f"&styles=&format=image/geotiff"
        f"&crs=EPSG:4326"
        f"&bbox={south},{west},{north},{east}"
        f"&width={width}&height={height}"
    )

    response = requests.get(wms_url)
    response.raise_for_status()

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        tmp.write(response.content)
        tmp.flush()

        with rasterio.open(tmp.name) as src:
            data = src.read(1)
            row, col = src.index(lon, lat)
            value = data[row, col]
            return float(value * 80) if np.isfinite(value) else None
