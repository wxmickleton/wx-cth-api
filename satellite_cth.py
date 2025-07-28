import requests
import rasterio
import numpy as np
import tempfile

def get_cloud_top_height(lat, lon): # 100 sq miles @ mid lats so 10 miles n,e,s,w aka metar vc
    width = 256
    height = 256
    south = lat - 0.145
    north = lat + 0.145
    west = lon - 0.205
    east = lon + 0.205

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

    with tempfile.NamedTemporaryFile(delete=False, suffix=".tif") as tmp:
        tmp.write(response.content)
        tmp.flush()

        with rasterio.open(tmp.name) as src:
            data = src.read(1)
            valid_data = data[(data > 0) & (data < 255)]
            scaled_data = (valid_data.astype(np.float64) * 61.7) + 258.3 # do NOT use 320 - that is not correct as BIDMAS, 258.3 is an offset!
            return float(np.max(scaled_data))
