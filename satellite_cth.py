import eumdac, xarray as xr, numpy as np, tempfile, shutil, zipfile, os
from datetime import datetime, timedelta


def get_cloud_top_height(lat: float, lon: float, key: str, secret: str, *, hours_back: int = 2) -> float | None:
    """Return cloud‑top height (m) at the nearest pixel to *lat*, *lon*.

    Args:
        lat, lon : target latitude / longitude in degrees.
        key, secret : long‑lived EUMETSAT API credentials.
        hours_back : how far back to search for a product (default 2 h).

    Returns:
        Cloud‑top height in metres (float) or **None** if no product found.
    """

    # 1 · authenticate and open collection
    token = eumdac.AccessToken((key, secret))
    store = eumdac.DataStore(token)
    coll  = store.get_collection("EO:EUM:DAT:MSG:CTH")

    # 2 · get latest product in time window
    now = datetime.utcnow()
    prod_iter = coll.search(dtstart=now - timedelta(hours=hours_back), dtend=now)
    product = next(iter(prod_iter), None)
    if product is None:
        return None

    # 3 · download ZIP to a disposable folder
    with tempfile.TemporaryDirectory() as tmp:
        zip_file = os.path.join(tmp, "cth.zip")
        with product.open() as remote, open(zip_file, "wb") as local:
            shutil.copyfileobj(remote, local)

        # 4 · extract GRIB file
        with zipfile.ZipFile(zip_file) as z:
            z.extractall(tmp)
        grib_name = next(p for p in os.listdir(tmp) if p.endswith(".grb"))
        grib_path = os.path.join(tmp, grib_name)

        # 5 · open GRIB + find nearest pixel
        ds = xr.open_dataset(grib_path, engine="cfgrib")
        lat_arr = ds.latitude.values
        lon_arr = ds.longitude.values
        cth_arr = ds.ctoph.values

        idx = np.argmin((lat_arr - lat) ** 2 + (lon_arr - lon) ** 2)
        return int(round(float(cth_arr[idx]), 2))


# ── simple CLI test ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse, getpass

    parser = argparse.ArgumentParser(description="Fetch Cloud‑Top Height at a point")
    parser.add_argument("lat", type=float, help="Latitude in degrees")
    parser.add_argument("lon", type=float, help="Longitude in degrees")
    parser.add_argument("--key", required=False, help="EUMETSAT API key")
    parser.add_argument("--secret", required=False, help="EUMETSAT API secret")
    args = parser.parse_args()

    key = args.key or getpass.getpass("API key: ")
    secret = args.secret or getpass.getpass("API secret: ")

    value = get_cloud_top_height(args.lat, args.lon, key, secret)
    print("CTH:", value)
