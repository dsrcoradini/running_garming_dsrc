"""
Tests for helper functions.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from running_analyzer.utils import format_run_name, format_pace, format_distance, format_duration


def test_format_run_name():
    """Test run name formatting."""
    result = format_run_name("running_2025-09-18_16-28-28_20428981613")
    assert result == "18/09/2025 16:28"
    
    # Test fallback
    result = format_run_name("invalid_name")
    assert result == "invalid_name"


def test_format_pace():
    """Test pace formatting."""
    assert format_pace(330) == "5:30/km"
    assert format_pace(300) == "5:00/km"
    assert format_pace(0) == "N/A"
    assert format_pace(None) == "N/A"


def test_format_distance():
    """Test distance formatting."""
    assert format_distance(5000) == "5.00 km"
    assert format_distance(5234) == "5.23 km"
    assert format_distance(0) == "0.00 km"
    assert format_distance(None) == "N/A"


def test_format_duration():
    """Test duration formatting."""
    assert format_duration(3665) == "1:01:05"
    assert format_duration(125) == "2:05"
    assert format_duration(0) == "0:00"
    assert format_duration(None) == "N/A"


if __name__ == "__main__":
    test_format_run_name()
    test_format_pace()
    test_format_distance()
    test_format_duration()
    print("✅ All tests passed!")
