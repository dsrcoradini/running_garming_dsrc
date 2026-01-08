"""
Metrics calculations for running data (HRV, pace, statistics).
"""

import pandas as pd
import numpy as np


def add_hrv_metrics(df, window=10, method="std"):
    """
    Add HRV (Heart Rate Variability) metrics to DataFrame.
    
    Args:
        df: DataFrame with hr_bpm column
        window: Rolling window size for calculation
        method: 'std' for standard deviation or 'rmssd' for RMSSD
        
    Returns:
        DataFrame with hrv column added
    """
    df = df.copy()

    if method == "std":
        df["hrv"] = df["hr_bpm"].rolling(window=window).std()

    elif method == "rmssd":
        diffs = df["hr_bpm"].diff()
        df["hrv"] = np.sqrt((diffs**2).rolling(window=window).mean())

    return df


def add_pace_metrics(df):
    """
    Add pace metrics (min/km) to DataFrame.
    
    Args:
        df: DataFrame with timestamp and distance_m columns
        
    Returns:
        DataFrame with pace columns added
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["dt"] = df["timestamp"].diff().dt.total_seconds()
    df["dd"] = df["distance_m"].diff()
    df["pace_sec_per_km"] = df["dt"] / (df["dd"] / 1000)
    df["pace_min_per_km"] = df["pace_sec_per_km"] / 60
    return df


def compute_run_stats(df):
    """
    Compute summary statistics for a run.
    
    Args:
        df: DataFrame with running data
        
    Returns:
        Dictionary with distance_km, avg_hr, and avg_pace
    """
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
