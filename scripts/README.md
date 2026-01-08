# Scripts

Command-line utilities for the project.

## 📥 download_garmin.py

Interactive script to download FIT files from Garmin Connect.

### Basic Usage

```bash
# Interactive mode (recommended)
python scripts/download_garmin.py

# With environment variables
export GARMIN_EMAIL="your_email@example.com"
export GARMIN_PASSWORD="your_password"
python scripts/download_garmin.py
```

### Programmatic Usage

```python
from running_analyzer.downloader import download_activities

# Simple download
count = download_activities(
    email="your_email@example.com",
    password="your_password",
    output_dir="data/fit_files",
    activity_type="running",
    limit=20
)

print(f"Downloaded {count} activities")
```

### Features

- ✅ Interactive download with menu
- ✅ Filter by activity type
- ✅ Environment variables support
- ✅ Detailed progress logs
- ✅ Robust error handling

## 🔧 Creating New Scripts

When creating new scripts, follow this pattern:

```python
#!/usr/bin/env python3
"""
Script description.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from running_analyzer import ...

def main():
    # Script logic
    pass

if __name__ == "__main__":
    main()
```

### Principles:

1. **Business logic** → `src/running_analyzer/`
2. **CLI interface** → `scripts/`
3. **Scripts should be simple** - just user interface
4. **Reusable code** - modules can be imported

### Example Structure:

```
scripts/
├── __init__.py
├── README.md              # This file
├── download_garmin.py     # Garmin Connect downloader
└── your_script.py         # Your new script
```

## 📚 Available Scripts

### download_garmin.py

Download FIT files from Garmin Connect API.

**Use cases:**
- Batch download running activities
- Download specific activity types
- Filter and download by criteria

**Requirements:**
- `garminconnect` package: `pip install garminconnect`
- Valid Garmin Connect account

## 💡 Tips

1. **Use environment variables** for credentials to avoid typing them repeatedly
2. **Create `.env` file** from `.env.example` for local development
3. **Check logs** for detailed information about downloads
4. **Use programmatic API** when you need custom filtering logic

## 🐛 Troubleshooting

**Authentication fails:**
- Check your email and password
- Verify your Garmin Connect account is active
- Try logging in to Garmin Connect website first

**Download fails:**
- Check your internet connection
- Verify the output directory has write permissions
- Check if activities exist in your account

**Import errors:**
- Make sure you're running from project root
- Activate virtual environment: `source .venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`
