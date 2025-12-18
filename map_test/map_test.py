import plotly.express as px
import os
import sys
import numpy as np
import pandas as pd

# Add parent folder to Python path
sys.path.append(r"C:\Users\diego\project1")

from coordinates import bounding_boxes  # your bounding box definitions

data_folder = r"C:\Users\diego\project1\csv_file"
file_names = os.listdir(data_folder)

all_runs = []

for name in file_names:
    # Only process files that truly end with .csv
    if not name.lower().endswith(".csv"):
        print(f"Skipping non‑CSV file: {name}")
        continue

    csv_path = os.path.join(data_folder, name)

    # Skip empty files
    if os.path.getsize(csv_path) == 0:
        print(f"Skipping empty file: {name}")
        continue

    try:
        df = pd.read_csv(csv_path)

        # Check required columns
        if {'latitude', 'longitude'}.issubset(df.columns):
            df['hrv_rolling'] = df['hr_bpm'].rolling(window=10).std()
            diffs = df['hr_bpm'].diff()
            df['hrv_rmssd'] = np.sqrt((diffs**2).rolling(window=10).mean())
            df['hrv_diff'] = df['hr_bpm'].diff()
            name = f'avg_hrv = {round(df["hrv_rmssd"].mean(),1)}, avg_hpm is {round(df["hr_bpm"].mean(),2)}'
            df['run_name'] = name
            all_runs.append(df)
        else:
            print(f"Skipping {name}: missing latitude/longitude columns")

    except pd.errors.EmptyDataError:
        print(f"Skipping {name}: not a valid CSV (EmptyDataError)")
    except Exception as e:
        print(f"Error reading {name}: {e}")

# Merge all valid runs
if all_runs:
    df_all = pd.concat(all_runs, ignore_index=True)
    print("Merged runs:", df_all.shape)
else:
    print("No valid runs found")

# --- Use bounding box from coordinates.py ---
def expand_bbox_with_tolerance(df, bbox, tol_lat=0.01, tol_lon=0.01):
    """
    Expand bounding box if run points fall slightly outside.
    tol_lat, tol_lon = tolerance in degrees (~0.01° ≈ 1.1 km latitude)
    """
    lat_min, lat_max = bbox["lat_min"], bbox["lat_max"]
    lon_min, lon_max = bbox["lon_min"], bbox["lon_max"]

    # Check min/max from run
    run_lat_min, run_lat_max = df['latitude'].min(), df['latitude'].max()
    run_lon_min, run_lon_max = df['longitude'].min(), df['longitude'].max()

    # Expand only if within tolerance
    if run_lat_min < lat_min and abs(run_lat_min - lat_min) <= tol_lat:
        lat_min = run_lat_min
    if run_lat_max > lat_max and abs(run_lat_max - lat_max) <= tol_lat:
        lat_max = run_lat_max
    if run_lon_min < lon_min and abs(run_lon_min - lon_min) <= tol_lon:
        lon_min = run_lon_min
    if run_lon_max > lon_max and abs(run_lon_max - lon_max) <= tol_lon:
        lon_max = run_lon_max

    return {"lat_min": lat_min, "lat_max": lat_max,
            "lon_min": lon_min, "lon_max": lon_max}

# Start with Leoben bounding box
bbox_leoben = bounding_boxes["Austria"]["Leoben"]

# Expand with tolerance if needed
bbox_expanded = expand_bbox_with_tolerance(df_all, bbox_leoben, tol_lat=0.01, tol_lon=0.01)

# Filter data
df_selected = df_all[
    (df_all['latitude'].between(bbox_expanded["lat_min"], bbox_expanded["lat_max"])) &
    (df_all['longitude'].between(bbox_expanded["lon_min"], bbox_expanded["lon_max"]))
]

# Plotting every run in one map
fig = px.scatter_mapbox(
    df_selected,   # <-- corrected: use df_selected
    lat="latitude",
    lon="longitude",
    color="run_name",   # different color per run
    title="Runs in Leoben",   # dynamic title possible
    zoom=12,
    height=600
)

# Compute center automatically from bounding box
center_lat = (bbox_expanded["lat_min"] + bbox_expanded["lat_max"]) / 2
center_lon = (bbox_expanded["lon_min"] + bbox_expanded["lon_max"]) / 2

# Set basemap style
fig.update_layout(
    mapbox_style="open-street-map",   # free basemap
    mapbox_center={"lat": center_lat, "lon": center_lon}
)

fig.show()