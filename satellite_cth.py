import requests
from PIL import Image
from io import BytesIO
import numpy as np

def get_cloud_top_height(lat, lon): # 100 sq miles @ mid lats so 10 miles n,e,s,w aka metar vc
    rgb_colors = [
        (0, 0, 0), (26, 11, 0), (53, 23, 0), (79, 35, 0), (105, 45, 5),
        (122, 36, 42), (140, 27, 79), (157, 18, 117), (174, 9, 154), (192, 0, 192),
        (154, 0, 204), (117, 0, 216), (79, 0, 229), (41, 0, 241), (4, 1, 253),
        (0, 19, 255), (0, 45, 255), (0, 69, 255), (0, 95, 255), (0, 121, 255),
        (0, 146, 255), (0, 169, 255), (0, 194, 255), (0, 220, 255), (0, 244, 255),
        (0, 248, 226), (0, 235, 177), (0, 224, 128), (0, 211, 77), (0, 198, 27),
        (10, 194, 0), (34, 200, 0), (60, 206, 0), (83, 212, 0), (109, 219, 0),
        (134, 225, 0), (159, 231, 0), (184, 237, 0), (208, 243, 0), (233, 249, 0),
        (254, 251, 0), (254, 226, 0), (254, 201, 0), (254, 177, 0), (254, 152, 0),
        (254, 128, 0), (254, 102, 0), (254, 77, 0), (254, 53, 0), (254, 28, 0),
        (254, 3, 0), (238, 26, 26), (219, 57, 57), (201, 88, 88), (183, 120, 120),
        (166, 150, 150), (169, 169, 169), (181, 181, 181), (193, 193, 193),
        (205, 205, 205), (218, 218, 218), (230, 230, 230), (243, 243, 243),
        (255, 255, 255),
    ]
    
    def find_nearest_rgb(color, palette):
        distances = [np.sum((np.array(color) - np.array(p))**2) for p in palette]
        return palette[np.argmin(distances)]
    
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
    image = Image.open(BytesIO(response.content)).convert("RGB")
    
    pixels = list(image.getdata())
    unique_colors = set(pixels)
    
    color_map = {}
    for color in unique_colors:
        if color in rgb_colors:
            color_map[color] = color
        else:
            nearest = find_nearest_rgb(color, rgb_colors)
            color_map[color] = nearest
    
    used_colors = set(color_map.values())
    
    deepest_index = -1
    for idx, color in enumerate(rgb_colors):
        if color in used_colors:
            deepest_index = idx + 1
            
    return((deepest_index * 245) + 320)
