#!/usr/bin/env python3
"""
CLI script to download FIT files from Garmin Connect.

Usage:
    python scripts/download_garmin.py
    
Environment variables:
    GARMIN_EMAIL: Garmin Connect email
    GARMIN_PASSWORD: Garmin Connect password
    RUN_FIT_FOLDER: Output directory (default: data/fit_files)
"""

import os
import sys
import logging
from pathlib import Path
from getpass import getpass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from running_analyzer.downloader import GarminDownloader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger(__name__)


def get_credentials():
    """Get Garmin credentials from environment or user input."""
    email = os.getenv("GARMIN_EMAIL")
    password = os.getenv("GARMIN_PASSWORD")
    
    if not email:
        email = input("Enter Garmin email: ").strip()
    
    if not password:
        password = getpass("Enter Garmin password: ")
    
    return email, password


def get_output_directory():
    """Get output directory from environment or use default."""
    default_dir = Path(__file__).parent.parent / "data" / "fit_files"
    output_dir = Path(os.getenv("RUN_FIT_FOLDER", default_dir))
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def interactive_menu():
    """Interactive menu for downloading activities."""
    logger.info("=" * 60)
    logger.info("🚴 Garmin Connect FIT Downloader")
    logger.info("=" * 60)
    
    # Get credentials
    email, password = get_credentials()
    output_dir = get_output_directory()
    
    logger.info(f"\n📁 Output directory: {output_dir}")
    
    # Initialize downloader
    downloader = GarminDownloader(email, password, output_dir)
    
    if not downloader.authenticate():
        logger.error("\n❌ Authentication failed. Exiting.")
        return 1
    
    # Main loop
    while True:
        logger.info("\n" + "=" * 60)
        logger.info("OPTIONS:")
        logger.info("  1. Download activities by type")
        logger.info("  2. Download recent activities (all types)")
        logger.info("  3. Change output directory")
        logger.info("  q. Quit")
        logger.info("=" * 60)
        
        choice = input("\nSelect an option: ").strip().lower()
        
        if choice == "1":
            activity_type = input("\nEnter activity type (e.g., running, cycling, hiking): ").strip()
            limit_str = input("How many recent activities? (default 20): ").strip()
            limit = int(limit_str) if limit_str.isdigit() else 20
            
            downloader.download_activities_batch(activity_type, limit)
            
        elif choice == "2":
            limit_str = input("\nHow many recent activities? (default 20): ").strip()
            limit = int(limit_str) if limit_str.isdigit() else 20
            
            downloader.download_activities_batch(activity_type=None, limit=limit)
            
        elif choice == "3":
            new_dir = input("\nEnter new output directory: ").strip()
            output_dir = Path(new_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            downloader.output_dir = output_dir
            logger.info(f"✅ Output directory changed to: {output_dir}")
            
        elif choice == "q":
            logger.info("\n👋 Goodbye!")
            break
            
        else:
            logger.warning("❌ Invalid choice. Try again.")
    
    return 0


def main():
    """Main entry point."""
    try:
        sys.exit(interactive_menu())
    except KeyboardInterrupt:
        logger.info("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
