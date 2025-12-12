import pandas as pd
import numpy as np
import seaborn as sns
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

#organizing zones as percentages overall the exercises

#function to filter only the wished dataset. Distance needs to be written in meter 
def run_df(dic_data_list, dis_max, dis_min):
    results = []
    for item in dic_data_list: 
        if dis_min <= item["Distance"] <= dis_max:
            results.append(item["Dfs"])
    return results

results = run_df(dic_data_list,16000,14000)
#plotting an histogram

def hist_run_hrzone(results):
    zone_order = ["zone_1","zone_2","zone_3","zone_4","zone_5"]
    colors = ["red","blue","green","orange","purple","cyan","magenta","brown","gray","olive"]

    for idx, daframe in enumerate(results):
        counts = daframe["hrzone"].value_counts().reindex(zone_order, fill_value=0)
        temp = counts.reset_index()
        temp.columns = ["hrzone", "count"]
        temp["run"] = f"Run {idx+1}"
        #plt grouped bars
        sns.barplot(x="hrzone", y="count", data=temp, label=f"Run {idx+1}", order=zone_order,color= colors[idx%len(colors)], edgecolor="black")
    plt.title("Heart Rate Zone Comparison Across Runs")
    plt.xlabel("Heart Rate Zone")
    plt.ylabel("Count (≈ time)")
    plt.legend(title = "Run", ncol=2) #legend with multiple column for readability
    plt.show()


hist_run_hrzone(results)