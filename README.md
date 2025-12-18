This project is a data analysis test. It consists of three main components: the API, the CSV converter, and the analyser.

**API – api_call_fit_file**  
Located in the project1 root folder.  
This script retrieves FIT data from Garmin and downloads it to your computer or repository.  
You must provide your email and password, but credentials are not stored.  
The API supports downloading up to 1000 activities. A potential improvement would be to define a date window for more precise filtering.

**CSV Converter – convert_fit_to_csv**  
Located in the fit_file folder.  
This script converts FIT files to CSV format. The current version focuses on a few metrics (time, heart rate, distance).  
Depending on your watch or gadgets, you can modify the code to extract additional metrics if needed.

**Analyser – analyser.py** --> Is not being used might be discontinued  
Currently, the analyser groups runs into specific categories.  
Future work will explore more innovative approaches for deeper data analysis.

**Mapping & HRV – map_test.py
Located in the map_test folder.
This script merges multiple CSV runs and filters them using bounding boxes defined in a separate coordinates.py file.
- Bounding boxes are stored per city/country, allowing flexible filtering of runs by location.
- A tolerance expansion method is implemented: if a run slightly exceeds the bounding box, the box expands within a defined threshold.
- Runs can be filtered across multiple cities by combining bounding boxes.
- Visualizations are generated with Plotly (scatter_mapbox), showing each run with a distinct color.
Additionally, the script computes Heart Rate Variability (HRV) metrics directly from the CSV data:
- hrv_rolling: rolling standard deviation of heart rate (hr_bpm).
- hrv_rmssd: Root Mean Square of Successive Differences (RMSSD), a standard HRV measure.
- hrv_diff: raw beat‑to‑beat differences for inspection.
These metrics are added as new columns to each run DataFrame, enabling deeper physiological analysis alongside geospatial visualization.



