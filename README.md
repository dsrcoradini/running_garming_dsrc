
Short purpose
- A personal project to visualize Garmin/FIT (or TCX) running data as an interactive Dash app.

What's in the repo
- `dash_board.py` — the Dash app.
- `api_call_fit_file.py` — helper functions for FIT/TCX handling (see files).
- `version_packages.txt` — currently listed package versions.
- Folders: `fit_folder`, `map_data`, `functions` (placeholders / helper functions expected).

Quickstart (recommended)
1. Clone the repo:
   ```
   git clone https://github.com/dsrcoradini/running_garming_dsrc.git
   cd running_garming_dsrc
   ```

2. Python environment:
   - Python 3.9+ recommended (check your dependencies).
   - Create a virtual environment:
     ```
     python -m venv .venv
     source .venv/bin/activate   # Linux / macOS
     .venv\Scripts\activate      # Windows
     ```

3. Install dependencies:
   - If you create a `requirements.txt`:
     ```
     pip install -r requirements.txt
     ```
   - Alternatively you can use `version_packages.txt` as a starting point:
     ```
     pip install -r version_packages.txt
     ```

4. Prepare data:
   - Place your (small) FIT or TCX files in `fit_folder/`.
   - Note: The code labels some TCX files as `.fit` — make sure the actual format is correct.

5. Start the app:
   ```
   python dash_board.py
   ```
   - By default Dash runs with `debug=True` — change to `False` for production.

Brief status of `dash_board.py`
- Functional: the app produces comparison plots and a map.
- Issues addressed in the refactor: removed hardcoded paths, added logging, modularized loading, added config via env var, and provided an app factory. Tests, further modularization and type annotations for functions in `functions/` are still recommended.

Next steps
- Fix city‑based filtering by improving bounding box expansion logic.
- Implement VO₂max estimation and fitness age models.
- Add dynamic comparison tools (distance‑aligned plots, smoothing options).
- Optional: Add support for true FIT files in the future

