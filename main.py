from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Query
from satellite_cth import get_cloud_top_height
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://wxmickleton.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/cth")
def fetch_cth(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180)
):
    # Read EUMETSAT credentials from environment
    key = "tfAcb1eGOgCs_vfJ4ghU9rKR2Fsa"
    secret = "x7CIX9YDGRCKX7HCvaJqLf7kBdoa"

    cth = get_cloud_top_height(lat, lon, key, secret)

    return {
        "cloud_top_height_m": cth
    }
