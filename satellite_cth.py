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
            valid_data = data[np.isfinite(data)]

            if valid_data.size == 0:
                return None
            scaled_data = valid_data.astype(np.float64) * 80
            print("Valid Cloud Top Heights (scaled, one per line):")
            return float(np.max(scaled_data))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Fetch Cloud Top Height (CTH)")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")

    args = parser.parse_args()
    cth = get_cloud_top_height(args.lat, args.lon)
    
    if cth is not None:
        print(f"Cloud Top Height: {cth:.2f} meters")
    else:
        print("No valid cloud top height data.")
