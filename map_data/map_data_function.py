import plotly.express as px
import os
import numpy as np
import pandas as pd

from functions.coordinates import bounding_boxes  # bounding box definitions

# ---------------------------------------------------------
# Bounding box expansion
# ---------------------------------------------------------
def expand_bbox_with_tolerance(df, bbox, tol_lat=0.01, tol_lon=0.01):
    """
    Expand bounding box if run points fall slightly outside.
    tol_lat, tol_lon = tolerance in degrees (~0.01° ≈ 1.1 km latitude)
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


# ---------------------------------------------------------
# Example usage (commented out - requires df_all to be passed)
# ---------------------------------------------------------
# bbox_leoben = bounding_boxes["Austria"]["Leoben"]
# bbox_expanded = expand_bbox_with_tolerance(
#     df_all, bbox_leoben, tol_lat=0.01, tol_lon=0.01
# )
# df_selected = df_all[
#     df_all["latitude"].between(bbox_expanded["lat_min"], bbox_expanded["lat_max"])
#     & df_all["longitude"].between(bbox_expanded["lon_min"], bbox_expanded["lon_max"])
# ]
