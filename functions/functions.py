import pandas as pd
import numpy as np
from fitparse import FitFile
import sys
import os
import xml.etree.ElementTree as ET

# ---------------------------------------------------------
# FIT → DataFrame loader (FULL Garmin Running Dynamics)
# ---------------------------------------------------------
def semicircles_to_degrees(x):
    if pd.isna(x):
        return np.nan
    return x * (180 / 2**31)


def load_fit_to_df(path):
    fit = FitFile(path)

    records = []
    for record in fit.get_messages("record"):
        data = {}
        for field in record:
            data[field.name] = field.value
        records.append(data)

    df = pd.DataFrame(records)

    # Convert GPS
    if "position_lat" in df.columns:
        df["latitude"] = df["position_lat"].apply(semicircles_to_degrees)
    if "position_long" in df.columns:
        df["longitude"] = df["position_long"].apply(semicircles_to_degrees)

    # Normalize field names
    df = df.rename(columns={
        "timestamp": "timestamp",
        "heart_rate": "hr_bpm",
        "distance": "distance_m",
        "speed": "speed_m_s",
        "cadence": "cadence_spm",
        "vertical_oscillation": "vertical_osc_mm",
        "stance_time": "ground_contact_time_ms",
        "stance_time_balance": "ground_contact_balance",
        "temperature": "temperature_c",
        "altitude": "elevation_m",
        "power": "power_w"
    })

    # Convert units
    if "vertical_osc_mm" in df.columns:
        df["vertical_osc_cm"] = df["vertical_osc_mm"] / 10

    if "ground_contact_time_ms" in df.columns:
        df["ground_contact_time_s"] = df["ground_contact_time_ms"] / 1000

    # Ensure timestamp is datetime
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    return df


# ---------------------------------------------------------
# Filter runs by city bounding box
# ---------------------------------------------------------
def filter_runs_by_city(runs, city, country_boxes):
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

# ---------------------------------------------------------
# Compute run summary stats
# ---------------------------------------------------------
def compute_run_stats(df):
    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["distance_m"] = pd.to_numeric(df["distance_m"], errors="coerce")

    df = df.dropna(subset=["timestamp", "distance_m"])

    total_time_sec = (df["timestamp"].iloc[-1] - df["timestamp"].iloc[0]).total_seconds()
    total_dist_m = df["distance_m"].iloc[-1] - df["distance_m"].iloc[0]

    avg_hr = df["hr_bpm"].mean()

    if total_dist_m > 0 and total_time_sec > 0:
        pace_sec_per_km = total_time_sec / (total_dist_m / 1000)
    else:
        pace_sec_per_km = float("nan")

    return {
        "distance_km": total_dist_m / 1000,
        "avg_hr": avg_hr,
        "avg_pace": pace_sec_per_km
    }


# ---------------------------------------------------------
# HRV metrics
# ---------------------------------------------------------
def add_hrv_metrics(df, window=10, method="std"):
    df = df.copy()

    if method == "std":
        df["hrv"] = df["hr_bpm"].rolling(window=window).std()

    elif method == "rmssd":
        diffs = df["hr_bpm"].diff()
        df["hrv"] = np.sqrt((diffs**2).rolling(window=window).mean())

    return df


# ---------------------------------------------------------
# Pace metrics (min/km)
# ---------------------------------------------------------
def add_pace_metrics(df):
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["dt"] = df["timestamp"].diff().dt.total_seconds()
    df["dd"] = df["distance_m"].diff()
    df["pace_sec_per_km"] = df["dt"] / (df["dd"] / 1000)
    df["pace_min_per_km"] = df["pace_sec_per_km"] / 60
    return df

##Bounding boxes
# Add parent folder to Python path
sys.path.append(r"C:\Users\diego\project1")
sys.path.append(r"C:\Users\diego\project1\functions")

from coordinates import bounding_boxes
from functions import load_fit_to_df   # <-- use FIT loader!


# ---------------------------------------------------------
# Load all FIT runs instead of CSVs
# ---------------------------------------------------------
def parse_tcx(filepath):
    ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    tree = ET.parse(filepath)
    root = tree.getroot()

    data = []
    for tp in root.findall('.//tcx:Trackpoint', ns):
        time = tp.find('tcx:Time', ns)
        hr = tp.find('.//tcx:HeartRateBpm/tcx:Value', ns)
        dist = tp.find('tcx:DistanceMeters', ns)
        pos = tp.find('tcx:Position', ns)

        lat = pos.find('tcx:LatitudeDegrees', ns) if pos is not None else None
        lon = pos.find('tcx:LongitudeDegrees', ns) if pos is not None else None

        # Optional fields
        cad = tp.find('tcx:Cadence', ns)
        ele = tp.find('tcx:AltitudeMeters', ns)
        temp = tp.find('tcx:Temperature', ns)

        if time is not None and hr is not None and lat is not None and lon is not None:
            data.append({
                "timestamp": time.text,
                "hr_bpm": int(hr.text),
                "distance_m": float(dist.text) if dist is not None else None,
                "latitude": float(lat.text),
                "longitude": float(lon.text),
                "cadence_spm": int(cad.text) if cad is not None else None,
                "elevation_m": float(ele.text) if ele is not None else None,
                "temperature_c": float(temp.text) if temp is not None else None,
            })

    df = pd.DataFrame(data)

    # Add empty columns for metrics TCX does NOT contain
    df["ground_contact_time_ms"] = None
    df["vertical_osc_mm"] = None
    df["power_w"] = None

    return df

# ---------------------------------------------------------
# Bounding box expansion
# ---------------------------------------------------------
def expand_bbox_with_tolerance(df, bbox, tol_lat=0.01, tol_lon=0.01):
    lat_min, lat_max = bbox["lat_min"], bbox["lat_max"]
    lon_min, lon_max = bbox["lon_min"], bbox["lon_max"]

    run_lat_min, run_lat_max = df["latitude"].min(), df["latitude"].max()
    run_lon_min, run_lon_max = df["longitude"].min(), df["longitude"].max()

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

