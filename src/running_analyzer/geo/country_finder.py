import os
import json
from shapely.geometry import Point, shape

# Path to THIS file's directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Full path to the GeoJSON file
GEOJSON_PATH = os.path.join(BASE_DIR, "countries.geojson")

with open(GEOJSON_PATH, "r", encoding="utf-8") as f:
    countries = json.load(f)
    
def get_country(lat, lon):
    point = Point(lon, lat)
    for feature in countries["features"]:
        polygon = shape(feature["geometry"])
        if polygon.contains(point):
            return feature["properties"]["name"]
    return None
