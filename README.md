# Running Garmin Data Visualization

Visualize Garmin/FIT and TCX running data with an interactive Dash dashboard. Compare runs, analyze metrics, and view routes on maps.

## ✨ Features

- 📊 Interactive dashboard with comparison plots
- 🗺️ Map visualization of running routes
- 💓 Metrics: HRV, pace, cadence, elevation, temperature
- 🏃 Running dynamics: ground contact time, vertical oscillation, power
- 🌍 Location filtering by country/city
- 📥 Garmin Connect API integration
- 📁 Supports FIT and TCX file formats

## 🚀 Quick Start

### Installation

```bash
# Clone repository
git clone https://github.com/dsrcoradini/running_garming_dsrc.git
cd running_garming_dsrc

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Optional: Install as package
pip install -e .
```

## 📖 Usage

### 1. Prepare Data

**Option A: Download from Garmin Connect (Interactive)**
```bash
# Interactive menu
python scripts/download_garmin.py

# Or with environment variables (no prompts)
export GARMIN_EMAIL="your_email@example.com"
export GARMIN_PASSWORD="your_password"
python scripts/download_garmin.py
```

**Option B: Programmatic Download**
```python
from running_analyzer.downloader import download_activities

count = download_activities(
    email="your_email@example.com",
    password="your_password",
    output_dir="data/fit_files",
    activity_type="running",
    limit=20
)
```

**Option C: Manual Upload**
Place FIT/TCX files in `data/fit_files/` directory

### 2. Run Dashboard

```bash
# Simple way
python run.py

# Or if installed as package
running-analyzer

# With custom data folder
export RUN_FIT_FOLDER=/path/to/your/fit/files
python run.py
```

Open `http://127.0.0.1:8050` in your browser.

### 3. Configuration (Optional)

Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

## 📁 Project Structure

```
running_garming_dsrc/
├── src/
│   └── running_analyzer/          # Main package
│       ├── __init__.py
│       ├── app.py                 # Dash application
│       ├── parsers/               # FIT/TCX parsers
│       │   ├── __init__.py
│       │   └── fit_parser.py
│       ├── metrics/               # Metrics calculations
│       │   ├── __init__.py
│       │   └── calculations.py
│       ├── geo/                   # Geographic filtering
│       │   ├── __init__.py
│       │   ├── coordinates.py
│       │   └── filters.py
│       ├── downloader/            # Garmin Connect API
│       │   ├── __init__.py
│       │   └── garmin_client.py
│       └── utils/                 # Helper functions
│           ├── __init__.py
│           └── helpers.py
├── scripts/                       # CLI scripts
│   ├── __init__.py
│   ├── download_garmin.py         # Download CLI
│   └── README.md                  # Scripts documentation
├── data/
│   └── fit_files/                 # FIT/TCX data files
├── examples/                      # Usage examples
│   └── download_example.py
├── tests/                         # Unit tests
│   ├── __init__.py
│   └── test_helpers.py
├── run.py                         # Entry point
├── setup.py                       # Package configuration
├── requirements.txt               # Dependencies
├── .env.example                   # Configuration template
├── .gitignore
├── README.md
└── LICENSE
```

## 🧪 Running Tests

```bash
# Run tests
python -m pytest tests/

# Or run individual test file
python tests/test_helpers.py
```

## 📋 Requirements

- Python 3.9+
- See `requirements.txt` for all dependencies
- Optional: `garminconnect` for API downloads

## ✅ Status

**Implemented:**
- ✅ Interactive Dash dashboard
- ✅ FIT/TCX file parsing
- ✅ Multiple metrics visualization
- ✅ Geographic filtering by city
- ✅ Garmin Connect integration
- ✅ Running dynamics metrics
- ✅ Modular code structure
- ✅ Helper functions
- ✅ Basic unit tests

**Known Issues:**
- City filtering bounding box logic could be improved
- TCX files may be mislabeled as `.fit`

## 🔮 Future Enhancements

- [ ] VO₂max estimation
- [ ] Distance-aligned plots
- [ ] More comprehensive unit tests
- [ ] Export data to CSV/JSON
- [ ] Training load analysis
- [ ] Performance trends over time

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
