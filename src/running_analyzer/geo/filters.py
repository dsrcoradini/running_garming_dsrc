"""
Geographic filtering functions for runs.
"""


def expand_bbox_with_tolerance(df, bbox, tol_lat=0.01, tol_lon=0.01):
    """
    Expand bounding box if run points fall slightly outside.
    
    Args:
        df: DataFrame with latitude and longitude columns
        bbox: Dictionary with lat_min, lat_max, lon_min, lon_max
        tol_lat: Tolerance in degrees latitude (~0.01° ≈ 1.1 km)
        tol_lon: Tolerance in degrees longitude
        
    Returns:
        Expanded bounding box dictionary
    """
    lat_min, lat_max = bbox["lat_min"], bbox["lat_max"]
    lon_min, lon_max = bbox["lon_min"], bbox["lon_max"]

    run_lat_min, run_lat_max = df["latitude"].min(), df["latitude"].max()
    run_lon_min, run_lon_max = df["longitude"].min(), df["longitude"].max()

    # Expand only if within tolerance
    if run_lat_min < lat_min and abs(run_lat_min - lat_min) <= tol_lat:
        lat_min = run_lat_min
    if run_lat_max > lat_max and abs(run_lat_max - lat_max) <= tol_lat:
        lat_max = run_lat_max
    if run_lon_min < lon_min and abs(run_lon_min - lon_min) <= tol_lon:
        lon_min = run_lon_min
    if run_lon_max > lon_max and abs(run_lon_max - lon_max) <= tol_lon:
        lon_max = run_lon_max

    return {
        "lat_min": lat_min,
        "lat_max": lat_max,
        "lon_min": lon_min,
        "lon_max": lon_max,
    }


def filter_runs_by_city(runs, city, country_boxes):
    """
    Filter runs by city bounding box with tolerance expansion.
    
    Args:
        runs: List of run dictionaries with 'name' and 'df' keys
        city: City name to filter by
        country_boxes: Dictionary of bounding boxes for cities
        
    Returns:
        List of filtered runs
    """
    bbox = country_boxes[city]
    filtered_runs = []

    for run in runs:
        df = run["df"]

        # Expand bounding box per run
        bbox_expanded = expand_bbox_with_tolerance(df, bbox)

        df_filtered = df[
            df["latitude"].between(bbox_expanded["lat_min"], bbox_expanded["lat_max"]) &
            df["longitude"].between(bbox_expanded["lon_min"], bbox_expanded["lon_max"])
        ]

        if not df_filtered.empty:
            filtered_runs.append({"name": run["name"], "df": df_filtered})

    return filtered_runs
