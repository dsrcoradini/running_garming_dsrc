"""
FIT and TCX file parsers for running data.
"""

import pandas as pd
import numpy as np
from fitparse import FitFile
import xml.etree.ElementTree as ET


def semicircles_to_degrees(x):
    """Convert Garmin semicircles to degrees."""
    if pd.isna(x):
        return np.nan
    return x * (180 / 2**31)


def load_fit_to_df(path):
    """
    Load FIT file and convert to DataFrame with full Garmin Running Dynamics.
    
    Args:
        path: Path to FIT file
        
    Returns:
        DataFrame with running data
    """
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


def parse_tcx(filepath):
    """
    Parse TCX file and convert to DataFrame.
    
    Args:
        filepath: Path to TCX file
        
    Returns:
        DataFrame with running data
    """
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
