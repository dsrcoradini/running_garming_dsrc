"""
Garmin Connect API client for downloading activities.
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class GarminDownloader:
    """
    Client for downloading FIT files from Garmin Connect.
    """
    
    def __init__(self, email: str, password: str, output_dir: Path):
        """
        Initialize Garmin downloader.
        
        Args:
            email: Garmin Connect email
            password: Garmin Connect password
            output_dir: Directory to save FIT files
        """
        self.email = email
        self.password = password
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.api = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with Garmin Connect.
        
        Returns:
            True if authentication successful, False otherwise
        """
        try:
            from garminconnect import Garmin, GarminConnectAuthenticationError
            
            self.api = Garmin(self.email, self.password)
            self.api.login()
            logger.info("✅ Logged in to Garmin Connect")
            return True
        except GarminConnectAuthenticationError:
            logger.error("❌ Authentication failed. Check your credentials.")
            return False
        except ImportError:
            logger.error("❌ garminconnect package not installed. Run: pip install garminconnect")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during authentication: {e}")
            return False
    
    def get_activities(
        self, 
        activity_type: Optional[str] = None, 
        limit: int = 20
    ) -> List[Dict]:
        """
        Fetch activities from Garmin Connect.
        
        Args:
            activity_type: Filter by activity type (e.g., 'running', 'cycling')
            limit: Maximum number of activities to fetch
            
        Returns:
            List of activity dictionaries
        """
        if not self.api:
            logger.error("Not authenticated. Call authenticate() first.")
            return []
        
        try:
            logger.info(f"🔍 Fetching up to {limit} activities...")
            activities = self.api.get_activities(0, limit)
            
            if activity_type:
                activities = [
                    act for act in activities 
                    if act["activityType"]["typeKey"].lower() == activity_type.lower()
                ]
                logger.info(f"📋 Found {len(activities)} '{activity_type}' activities")
            else:
                logger.info(f"📋 Found {len(activities)} activities")
            
            return activities
        except Exception as e:
            logger.error(f"❌ Error fetching activities: {e}")
            return []
    
    def download_activity(self, activity_id: int, filename: str) -> bool:
        """
        Download a single activity as FIT file.
        
        Args:
            activity_id: Garmin activity ID
            filename: Output filename (without path)
            
        Returns:
            True if download successful, False otherwise
        """
        if not self.api:
            logger.error("Not authenticated. Call authenticate() first.")
            return False
        
        try:
            fit_path = self.output_dir / filename
            fit_data = self.api.download_activity(activity_id)
            
            with open(fit_path, "wb") as f:
                f.write(fit_data)
            
            logger.info(f"✅ Downloaded: {filename}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to download activity {activity_id}: {e}")
            return False
    
    def download_activities_batch(
        self, 
        activity_type: str = "running", 
        limit: int = 20,
        show_details: bool = True
    ) -> int:
        """
        Download multiple activities in batch.
        
        Args:
            activity_type: Type of activities to download
            limit: Maximum number to fetch
            show_details: Show activity details before downloading
            
        Returns:
            Number of successfully downloaded activities
        """
        activities = self.get_activities(activity_type, limit)
        
        if not activities:
            logger.warning("⚠️ No activities found to download")
            return 0
        
        # Show activity details
        if show_details:
            logger.info("\n📋 Activities to download:")
            for i, act in enumerate(activities, 1):
                act_id = act["activityId"]
                act_type = act["activityType"]["typeKey"]
                act_date = act["startTimeLocal"]
                act_name = act.get("activityName", "Unnamed")
                distance = round(act.get("distance", 0) / 1000, 2)
                duration = round(act.get("duration", 0) / 60, 1)
                logger.info(
                    f"{i:2}. ID: {act_id} | {act_type} | {act_date} | "
                    f"{act_name} | {distance} km in {duration} min"
                )
        
        # Download activities
        logger.info(f"\n📦 Starting download of {len(activities)} activities...")
        success_count = 0
        
        for act in activities:
            activity_id = act["activityId"]
            start_time = act["startTimeLocal"].replace(":", "-").replace(" ", "_")
            filename = f"{activity_type}_{start_time}_{activity_id}.fit"
            
            if self.download_activity(activity_id, filename):
                success_count += 1
        
        logger.info(f"\n✅ Successfully downloaded {success_count}/{len(activities)} activities")
        return success_count


def download_activities(
    email: str,
    password: str,
    output_dir: Path,
    activity_type: str = "running",
    limit: int = 20
) -> int:
    """
    Convenience function to download activities.
    
    Args:
        email: Garmin Connect email
        password: Garmin Connect password
        output_dir: Directory to save FIT files
        activity_type: Type of activities to download
        limit: Maximum number to fetch
        
    Returns:
        Number of successfully downloaded activities
    """
    downloader = GarminDownloader(email, password, output_dir)
    
    if not downloader.authenticate():
        return 0
    
    return downloader.download_activities_batch(activity_type, limit)
