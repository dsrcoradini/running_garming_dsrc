"""
Garmin Connect downloader module.
"""

from running_analyzer.downloader.garmin_client import (
    GarminDownloader,
    download_activities,
)

__all__ = [
    'GarminDownloader',
    'download_activities',
]
