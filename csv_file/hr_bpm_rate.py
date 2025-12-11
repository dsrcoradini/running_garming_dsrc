import pandas as pd
import numpy as np
import os 
from pathlib import Path
import matplotlib.pyplot as plt


folder_path = Path(r"C:\Users\diego\project1\csv_file")
file_list = folder_path.glob("*.csv")
print(file_list)

dic_data_list = [] #declaring the dictionary
#organizing the whole dataset in a dictionary
for file in file_list:
    #loading the dataframe
    df = pd.read_csv(file)
    df["hr_diff"] = df["hr_bpm"].diff()
    time_str = df["time_s"].iloc[0] #finding one date value
    #appending values to the dictionary
    dic_data_list.append({
        "Distance": round(df["d_meter_m"].max(),1),
        "Date": time_str.split("T")[0],
        "Dfs": df
    })

#function creates categorical variables
def finding_zones(hr_max, dic_data_list):
    bins = [0, hr_max*0.6, hr_max*0.7, hr_max*0.8, hr_max*0.9, hr_max]
    labels = ["zone_1","zone_2","zone_3","zone_4","zone_5"]
    for item in dic_data_list:
        df = item["Dfs"] #accessing the dataframe
        df["hrzone"] = pd.cut(df["hr_bpm"], bins= bins, labels = labels)
        item["Dfs"] = df #updating back into the dictionary
    return dic_data_list

finding_zones(200,dic_data_list)