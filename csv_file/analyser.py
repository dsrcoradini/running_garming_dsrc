#example
df = pd.read_csv("2025.08.30.csv")

hzmax = 210
hz_wp = hzmax*0.6  
hz_endu = hzmax*0.8 
hz_fatig = hzmax*0.9
#converting time float to strftime
df.time_s = pd.to_datetime(df.time_s)
df["time_sec"] = (df["time_s"] - df["time_s"].iloc[0]).dt.total_seconds()
print(df.time_sec)
plt.scatter(x=df["time_sec"] , y=df.hr_bpm, color='red', label='Heart Rate')
#plotting a straightline
plt.axhline(y=hz_wp, color="blue", linestyle="--", label="Warm-up Zone")
plt.axhline(y=hz_endu, color="green", linestyle="--", label="Endurance")
plt.axhline(y=hz_fatig, color="black", linestyle="--", label="Fatigue")
plt.xlabel("Time [s]")
plt.ylabel("Heart Rate [bpm]")
plt.legend()
plt.show()

hrv = np.std(df["hr_bpm"])  # simple HRV proxy
print("HRV (std):", hrv)

hr_diff = np.diff(df["hr_bpm"])
plt.plot(hr_diff)
plt.title("Heart Rate Change Between Samples")
plt.xlabel("Sample Index")
plt.ylabel("ΔHR (bpm)")
plt.grid(True)
plt.show()
