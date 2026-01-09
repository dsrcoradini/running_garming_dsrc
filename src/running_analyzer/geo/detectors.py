from running_analyzer.geo.coordinates import bounding_boxes
from running_analyzer.geo.country_finder import get_country
from running_analyzer.geo.cache import load_auto_cities, save_auto_cities

def find_city_in_boxes(lat,lon,boxes):
    for city, bbox in boxes.items():
        if (
            bbox["lat_min"] <= lat <= bbox["lat_max"] and
            bbox["lon_min"] <= lon <= bbox["lon_max"]
        ):
            return city
    return None

def create_small_bbox(lat,lon,size=0.01):
    """Create a small bounding box around a coordinate."""
    return {"lat_min": lat - size,"lat_max": lat + size,"lon_min": lon - size,"lon_max": lon + size,}

def detect_or_create_city(lat, lon, country):
    """
    Detect city using curated + cached boxes.
    If not found, create a new cached city.
    """
    curated = bounding_boxes.get(country, {})
    cache = load_auto_cities()
    cached_cities = cache.get(country, {})

    # 1. Try curated cities
    city = find_city_in_boxes(lat, lon, curated)
    if city:
        return city

    # 2. Try cached cities
    city = find_city_in_boxes(lat, lon, cached_cities)
    if city:
        return city

    # 3. Create new city automatically
    new_city_name = f"AutoCity_{lat:.4f}_{lon:.4f}"
    new_bbox = create_small_bbox(lat, lon)

    # Add to cache
    if country not in cache:
        cache[country] = {}
    cache[country][new_city_name] = new_bbox

    save_auto_cities(cache)

    return new_city_name

