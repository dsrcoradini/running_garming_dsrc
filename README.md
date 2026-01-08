This project is a data analysis test. It consists of three main components: the API, the CSV converter, and the analyser.

**API – api_call_fit_file**  
Located in the project1 root folder.  
This script retrieves FIT data from Garmin and downloads it to your computer or repository.  
You must provide your email and password, but credentials are not stored.  
The API supports downloading up to 1000 activities. A potential improvement would be to define a date window for more precise filtering.

**dash_board**  
Data Pipeline: All processing now happens directly from the TCX files.
There is no need to convert anything to CSV anymore — the dashboard loads, parses, and analyzes the raw TCX data on the fly.
Although the files carry a .fit extension, they are actually TCX XML files, so FIT parsing libraries are not required.

Metrics & Device Considerations: Some metrics (e.g., power, ground contact time, vertical oscillation) are not present in TCX files and would require true FIT files or a device that records these fields.
Cadence, elevation, and temperature may be available depending on the device model.
Garmin Forerunner 255 uses Smart Recording, meaning data points are captured only when movement changes significantly.
This results in irregular sampling intervals, which affects smoothing, pace calculations, and dynamic plots.

Data Quality: Data cleaning is still necessary. Outliers in heart rate, GPS, or distance can distort HRV, pace, and other derived metrics. A robust cleaning pipeline (filters, smoothing, interpolation) will be needed.

Current Limitations
- City selection: The geographic filtering works only for some files.
Likely due to bounding box mismatches or missing GPS points in certain TCX files.
- Dynamic diagrams: Multi‑run comparison plots need refinement, especially with irregular sampling.
- Advanced metrics:
- VO₂max estimation is not implemented yet.
- Fitness age calculation is pending.
- Running dynamics (GCT, VO, power) require real FIT files.
Next Steps
- Improve TCX parsing to support more optional fields (cadence, elevation, temperature).
- Add a data‑cleaning module (outlier removal, smoothing, interpolation).
- Fix city‑based filtering by improving bounding box expansion logic.
- Implement VO₂max estimation and fitness age models.
- Add dynamic comparison tools (distance‑aligned plots, smoothing options).
- Optional: Add support for true FIT files in the future

