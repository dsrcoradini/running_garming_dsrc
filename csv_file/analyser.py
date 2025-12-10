import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os 
from pathlib import Path

#example


#hzmax = 210
#hz_wp = hzmax*0.6  
#hz_endu = hzmax*0.8 
#hz_fatig = hzmax*0.9
#scrapped out code
    ##converting time float to strftime
    #df.time_s = pd.to_datetime(df.time_s)
    #df["time_sec"] = (df["time_s"] - df["time_s"].iloc[0]).dt.total_seconds()
    #print(df.time_sec)
    #plt.scatter(x=df["time_sec"] , y=df.hr_bpm, color='red', label='Heart Rate')
    #plotting a straightline
    #plt.axhline(y=hz_wp, color="blue", linestyle="--", label="Warm-up Zone")
    #plt.axhline(y=hz_endu, color="green", linestyle="--", label="Endurance")
    #plt.axhline(y=hz_fatig, color="black", linestyle="--", label="Fatigue")
    #plt.xlabel("Time [s]")
    #plt.ylabel("Heart Rate [bpm]")
    #plt.legend()
    #plt.show()

    #hrv = np.std(df["hr_bpm"])  # simple HRV proxy
    #print("HRV (std):", hrv)

#hr_diff = np.diff(df["hr_bpm"])
#scrapped out code
    #plt.plot(hr_diff)
    #plt.title("Heart Rate Change Between Samples")
    #plt.xlabel("Sample Index")
    #plt.ylabel("ΔHR (bpm)")
    #plt.xlabel("Time [s]")
    #plt.ylabel("Heart Rate [bpm]")
    #plt.grid(True)
    #plt.show()

## grouping similar runs
#Finding similar runs

#taking every possible run
folder_path = Path(r"C:\Users\diego\project1\csv_file")
file_list = folder_path.glob("*.csv")

#function organizing the runs in different groups
def organizing_distance(distance_max, distance_min, file_list): #distance needs to be given in meters
    list_distance = []
    for file in file_list:
        #Load data
        df = pd.read_csv(file)
        #print(df.head())
        #maximum distance
        distance = df["d_meter_m"].max() - df["d_meter_m"].min()
        if distance >= distance_min and distance < distance_max:
            list_distance.append(file)
    return list_distance        


def distance_plt(list_distance):
    for item in list_distance:
        #Load each CSV
        df = pd.read_csv(item)
        
        #Normalizing the scale (0-1)
        df["time_s"] = pd.to_datetime(df["time_s"], errors="coerce")
        df["time_abs"] = (df["time_s"] - df["time_s"].min()).dt.total_seconds()
        df["time_abs"] = df["time_abs"] / df["time_abs"].max()
        
        #taking date out of the time_s
        dt = pd.to_datetime(df["time_s"].iloc[2])
        
        #plot
        plt.plot(df['time_abs'], df.hr_bpm, label = dt.date())
    plt.xlabel("Time (scaled 0–1)")
    plt.ylabel("Heart rate [bpm]")
    plt.title("Comparison of Multiple running data")
    plt.legend(loc="center right", bbox_to_anchor=(-0.2, 0.5))
    plt.tight_layout()

    plt.show()

#example
distance = organizing_distance(10000,8000,file_list = file_list)
distance_plt(distance)


#time_s