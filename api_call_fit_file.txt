import os
from pathlib import Path
from getpass import getpass

from garminconnect import Garmin, GarminConnectAuthenticationError

# Configuration
EMAIL = os.getenv("EMAIL") or input("Enter Garmin email: ")
PASSWORD = os.getenv("PASSWORD") or getpass("Enter Garmin password: ")

FIT_DIR = Path("fit_folder")
FIT_DIR.mkdir(exist_ok=True)

# Authenticate
try:
    api = Garmin(EMAIL, PASSWORD)
    api.login()
    print("✅ Logged in to Garmin Connect.")
except GarminConnectAuthenticationError:
    print("❌ Authentication failed. Check your credentials.")
    exit(1)

# Batch download FIT files
def batch_download_fit_files(activity_type: str, limit: int = 20):
    print(f"\n🔍 Searching for '{activity_type}' activities (limit {limit})...")
    try:
        activities = api.get_activities(0, limit)
        matched = [act for act in activities if act["activityType"]["typeKey"].lower() == activity_type.lower()]
        if not matched:
            print("⚠️ No matching activities found.")
            return

        # 📝 Show selected activities
        print("\n📋 Selected Activities:")
        for i, act in enumerate(matched, 1):
            act_id = act["activityId"]
            act_type = act["activityType"]["typeKey"]
            act_date = act["startTimeLocal"]
            act_name = act.get("activityName", "Unnamed")
            distance = round(act.get("distance", 0) / 1000, 2)
            duration = round(act.get("duration", 0) / 60, 1)
            print(f"{i:2}. ID: {act_id} | Type: {act_type} | Date: {act_date} | Name: {act_name} | {distance} km in {duration} min")

        print(f"\n📦 Found {len(matched)} matching activities. Starting FIT download...")
        for act in matched:
            activity_id = act["activityId"]
            start_time = act["startTimeLocal"].replace(":", "-").replace(" ", "_")
            fit_filename = FIT_DIR / f"{activity_type}_{start_time}_{activity_id}.fit"

            try:
                fit_data = api.download_activity(activity_id)
                with open(fit_filename, "wb") as f:
                    f.write(fit_data)
                print(f"✅ FIT saved: {fit_filename.name}")
            except Exception as e:
                print(f"❌ Failed to download activity {activity_id}: {e}")
    except Exception as e:
        print(f"❌ Error fetching activities: {e}")

# Main Menu
def main_menu():
    while True:
        print("\n🚴 Garmin FIT Downloader")
        print("1. Download FIT files by activity type")
        print("q. Quit")
        choice = input("Select an option: ").strip().lower()

        if choice == "1":
            activity_type = input("Enter activity type (e.g., running, cycling, hiking): ").strip()
            limit = input("How many recent activities to check? (default 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            batch_download_fit_files(activity_type, limit)
        elif choice == "q":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Try again.")

# Run
if __name__ == "__main__":
    main_menu()