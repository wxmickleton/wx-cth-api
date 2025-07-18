import eumdac
import xarray as xr
import numpy as np
import tempfile
import shutil
import zipfile
import os
from datetime import datetime, timedelta

def parse_iso8601_z(ts: str) -> datetime:
    """Parses an ISO 8601 UTC timestamp like '2024-07-18T12:34:56Z'."""
    return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")

def get_cloud_top_height(lat: float, lon: float, key: str, secret: str, *, hours_back: int = 2) -> float | None:
    """Return cloud‑top height (m) at the nearest pixel to *lat*, *lon*."""

    # 1 · Authenticate and open collection
    token = eumdac.AccessToken((key, secret))
    store = eumdac.DataStore(token)
    coll = store.get_collection("EO:EUM:DAT:MSG:CTH")

    # 2 · Get most recent product in the time window
    now = datetime.utcnow()
    products = list(coll.search(dtstart=now - timedelta(hours=hours_back), dtend=now))
    if not products:
        return None

    # Sort products by 'endposition' timestamp from metadata
    product = max(products, key=lambda p: parse_iso8601_z(p.metadata["endposition"]))
    print(f"Using product from: {product.metadata['beginposition']} to {product.metadata['endposition']}")

    # 3 · Download ZIP to a temporary directory
    with tempfile.TemporaryDirectory() as tmp:
        zip_file = os.path.join(tmp, "cth.zip")
        with product.open() as remote, open(zip_file, "wb") as local:
            shutil.copyfileobj(remote, local)

        # 4 · Extract GRIB file
        with zipfile.ZipFile(zip_file) as z:
            z.extractall(tmp)
        grib_path = next(os.path.join(tmp, f) for f in os.listdir(tmp) if f.endswith(".grb"))

        # 5 · Open GRIB file and find nearest pixel
        ds = xr.open_dataset(grib_path, engine="cfgrib")
        lat_arr = ds.latitude.values
        lon_arr = ds.longitude.values
        cth_arr = ds.ctoph.values

        idx = np.argmin((lat_arr - lat) ** 2 + (lon_arr - lon) ** 2)
        return round(float(cth_arr[idx]), 2)

# ── Simple CLI test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import getpass

    parser = argparse.ArgumentParser(description="Fetch Cloud‑Top Height at a point")
    parser.add_argument("lat", type=float, help="Latitude in degrees")
    parser.add_argument("lon", type=float, help="Longitude in degrees")
    parser.add_argument("--key", required=False, help="EUMETSAT API key")
    parser.add_argument("--secret", required=False, help="EUMETSAT API secret")
    args = parser.parse_args()

    key = args.key or getpass.getpass("API key: ")
    secret = args.secret or getpass.getpass("API secret: ")

    value = get_cloud_top_height(args.lat, args.lon, key, secret)
    print("Cloud‑Top Height (m):", value)
