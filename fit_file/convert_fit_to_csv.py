#defining parse function for generating a heart rate vs distance log
def parsing_file(filepath):
    ns = {'tcx': 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'}
    tree = ET.parse(filepath)
    root = tree.getroot()

    data = []
    for trackpoint in root.findall('.//tcx:Trackpoint', ns):
        time = trackpoint.find('tcx:Time', ns)
        hr = trackpoint.find('.//tcx:HeartRateBpm/tcx:Value', ns)
        dist = trackpoint.find('tcx:DistanceMeters', ns)

        if time is not None and hr is not None:
            data.append({
                'time_s': time.text,
                'hr_bpm': int(hr.text),
                'd_meter_m': float(dist.text) if dist is not None else None
            })

    return pd.DataFrame(data)

#function save to excel 
def saving_excel(df, filename):
    folder = "csv_files"
    os.makedirs(folder, exist_ok=True)  # Create folder if it doesn't exist
    path = os.path.join(folder, filename)  # Full path to save
    try:
        df.to_csv(path, sep=',', index=False)
        if os.path.exists(path):
            print(f"✅ File saved successfully: {path}")
        else:
            print(f"⚠️ Save attempted but file not found: {path}")
    except Exception as e:
        print(f"❌ Error saving {path}: {e}")

#main loop
dfs_by_date = {}
file_names = os.listdir()

for name in file_names:
    if name.endswith(".fit") or name.endswith(".tcx"):
        try:
            df = parsing_file(name)
            date_str = pd.to_datetime(df["time_s"].iloc[0]).strftime("%Y.%m.%d")
        except Exception:
            date_str = name.replace(".fit", "").replace(".tcx", "")

        dfs_by_date[date_str] = df
        saving_excel(df, filename=f"{date_str}.csv")

# 4. Optional: print summary
print("\n📦 Summary of saved files:")
for date, df in dfs_by_date.items():
    print(f" - {date}.csv: {len(df)} rows")

