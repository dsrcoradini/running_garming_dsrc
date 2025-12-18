import os
import pandas as pd
import xml.etree.ElementTree as ET

# Define your data folder
data_folder = r"C:\Users\diego\project1\fit_file"

def parsing_file(filepath):
    ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    tree = ET.parse(filepath)
    root = tree.getroot()

    data = []
    for trackpoint in root.findall('.//tcx:Trackpoint', ns):
        time = trackpoint.find('tcx:Time', ns)
        hr = trackpoint.find('.//tcx:HeartRateBpm/tcx:Value', ns)
        dist = trackpoint.find('tcx:DistanceMeters', ns)
        pos = trackpoint.find('tcx:Position', ns)

        lat = pos.find('tcx:LatitudeDegrees', ns) if pos is not None else None
        lon = pos.find('tcx:LongitudeDegrees', ns) if pos is not None else None

        if time is not None and hr is not None and lat is not None and lon is not None:
            data.append({
                'time_s': time.text,
                'hr_bpm': int(hr.text),
                'd_meter_m': float(dist.text) if dist is not None else None,
                'latitude': float(lat.text),
                'longitude': float(lon.text)
            })
    return pd.DataFrame(data)

#adding heart rate variation, we are using 10 samples and 
def add_hrv(df, window=10, method="std"):
    if method == "std":
        df['hrv'] = df['hr_bpm'].rolling(window=window).std()
    elif method == "rmssd":
        diffs = df['hr_bpm'].diff()
        df['hrv'] = np.sqrt((diffs**2).rolling(window=window).mean())
    return df

def saving_excel(df, filename):
    folder = "csv_file"
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, filename)
    try:
        df.to_csv(path, sep=',', index=False)
        print(f"✅ File saved successfully: {path}")
    except Exception as e:
        print(f"❌ Error saving {path}: {e}")

# Main loop
dfs_by_date = {}
file_names = os.listdir(data_folder)
#print(file_names)

for name in file_names:
    #print(name)
    if name.endswith(".fit"):   # FIT files need a different parser
        filepath = os.path.join(data_folder, name)
        print(filepath)
        try:
            df = parsing_file(filepath)
            if not df.empty:
                date_str = pd.to_datetime(df["time_s"].iloc[0]).strftime("%Y.%m.%d")
            else:
                date_str = name.replace(".tcx", "")
        except Exception as e:
            print(f"⚠️ Error parsing {name}: {e}")
            df = pd.DataFrame()   # ensure df is defined
            date_str = name.replace(".tcx", "")

        dfs_by_date[date_str] = df
        saving_excel(df, filename=f"{date_str}.csv")

# Summary
print("\n📦 Summary of saved files:")
for date, df in dfs_by_date.items():
    print(f" - {date}.csv: {len(df)} rows")

