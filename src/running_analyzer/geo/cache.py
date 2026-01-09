import json
import os

CACHE_PATH = os.path.join(os.path.dirname(__file__), "auto_cities.json")


def load_auto_cities():
    """Load cached city bounding boxes from JSON."""
    if not os.path.exists(CACHE_PATH):
        return {}

    with open(CACHE_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}  # fallback if file is corrupted


def save_auto_cities(cache):
    """Save updated city bounding boxes to JSON."""
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=4)
