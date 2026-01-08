# Running Garmin Data Visualization

Visualize Garmin/FIT and TCX running data with an interactive Dash dashboard. Compare runs, analyze metrics, and view routes on maps.

## Features

- Interactive dashboard with comparison plots
- Map visualization of running routes
- Metrics: HRV, pace, cadence, elevation, temperature, running dynamics
- Location filtering by country/city
- Garmin Connect API integration for downloading activities
- Supports FIT and TCX file formats

## Installation

```bash
git clone https://github.com/dsrcoradini/running_garming_dsrc.git
cd running_garming_dsrc

python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

For Garmin Connect downloads:
```bash
pip install garminconnect
```

## Usage

### Prepare Data

**Option 1: Download from Garmin Connect**
```bash
python api_call_fit_file.py
```
Set `EMAIL` and `PASSWORD` environment variables or enter when prompted.

**Option 2: Manual**
Place FIT/TCX files in `fit_folder/`

### Run Dashboard

```bash
python dash_board.py
```

Open `http://127.0.0.1:8050` in your browser.

### Configuration

Set custom FIT folder location:
```bash
export RUN_FIT_FOLDER=/path/to/fit/files
```

## Project Structure

```
├── dash_board.py           # Main Dash app
├── api_call_fit_file.py    # Garmin Connect API
├── fit_folder/            # Place FIT/TCX files here
├── functions/
│   ├── functions.py       # Parsing and metrics
│   └── coordinates.py     # City bounding boxes
└── map_data/
    └── map_data_function.py
```

## Requirements

- Python 3.9+
- See `requirements.txt` for dependencies

## Status

**Working:**
- Dash app with plots and maps
- FIT/TCX parsing
- Multiple metrics visualization
- City filtering
- Garmin Connect integration

**Known Issues:**
- City filtering bounding box logic needs improvement
- TCX files may be mislabeled as `.fit`
- Debug mode enabled by default

## Future

- Improve city filtering logic
- VO₂max estimation
- Distance-aligned plots
- True FIT file parsing
- Unit tests
