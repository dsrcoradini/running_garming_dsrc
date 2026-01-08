"""
Helper functions for the running data visualization project.
"""

from datetime import datetime
from typing import Optional


def format_run_name(filename: str) -> str:
    """
    Convert filename like 'running_2025-09-18_16-28-28_20428981613'
    to readable format like '18/09/2025 16:28'
    
    Args:
        filename: The filename stem (without extension)
        
    Returns:
        Formatted readable name or original filename if parsing fails
    """
    try:
        # Extract date and time from filename
        # Format: running_YYYY-MM-DD_HH-MM-SS_ID
        parts = filename.split('_')
        if len(parts) >= 3:
            date_str = parts[1]  # 2025-09-18
            time_str = parts[2]  # 16-28-28
            
            # Parse date
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            # Parse time
            time_parts = time_str.split('-')
            
            # Format as "DD/MM/YYYY HH:MM"
            formatted = f"{date_obj.day:02d}/{date_obj.month:02d}/{date_obj.year} {time_parts[0]}:{time_parts[1]}"
            return formatted
    except Exception:
        pass
    
    # Fallback to original filename if parsing fails
    return filename


def format_pace(pace_seconds: float) -> str:
    """
    Convert pace in seconds per km to readable format 'MM:SS/km'
    
    Args:
        pace_seconds: Pace in seconds per kilometer
        
    Returns:
        Formatted pace string like "5:30/km"
    """
    if pace_seconds is None or pace_seconds <= 0:
        return "N/A"
    
    minutes = int(pace_seconds // 60)
    seconds = int(pace_seconds % 60)
    return f"{minutes}:{seconds:02d}/km"


def format_distance(distance_meters: float) -> str:
    """
    Convert distance in meters to readable format in kilometers
    
    Args:
        distance_meters: Distance in meters
        
    Returns:
        Formatted distance string like "5.2 km"
    """
    if distance_meters is None or distance_meters < 0:
        return "N/A"
    
    km = distance_meters / 1000
    return f"{km:.2f} km"


def format_duration(seconds: float) -> str:
    """
    Convert duration in seconds to readable format 'HH:MM:SS' or 'MM:SS'
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds is None or seconds < 0:
        return "N/A"
    
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"


def safe_mean(values, default: Optional[float] = None) -> Optional[float]:
    """
    Calculate mean safely, returning default if empty or all NaN
    
    Args:
        values: Array-like of values
        default: Default value to return if calculation fails
        
    Returns:
        Mean value or default
    """
    try:
        import numpy as np
        import pandas as pd
        
        if isinstance(values, (pd.Series, pd.DataFrame)):
            result = values.mean()
        else:
            result = np.nanmean(values)
            
        if pd.isna(result):
            return default
        return float(result)
    except Exception:
        return default
