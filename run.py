"""
Entry point for running the dash application.
This file maintains backward compatibility.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from running_analyzer.app import main

if __name__ == "__main__":
    main()
