#!/usr/bin/env python
# coding: utf-8

# In[7]:


import pandas as pd
import os
from datetime import datetime, timedelta

def load_and_calculate_dhw(project_root, base_subpath="data/raw/daily", days=84, threshold=1.0):
    base_path = os.path.join(project_root, base_subpath)
    end_date = datetime.utcnow().date() - timedelta(days=2)  # data availability delay
    start_date = end_date - timedelta(days=days-1)

    dfs = []

    for day_delta in range(days):
        date = start_date + timedelta(days=day_delta)
        folder = os.path.join(base_path, str(date.year), f"{date.month:02d}", f"{date.day:02d}")
        filename = f"sst_anomaly_{date.strftime('%Y_%m_%d')}.csv"
        filepath = os.path.join(folder, filename)

        if os.path.exists(filepath):
            df = pd.read_csv(filepath, skiprows=[1])
            df = df[['time', 'latitude', 'longitude', 'sea_surface_temperature_anomaly']]
            df['sea_surface_temperature_anomaly'] = pd.to_numeric(df['sea_surface_temperature_anomaly'], errors='coerce')
            dfs.append(df)
        else:
            print(f"Warning: Missing file {filepath}")

    if not dfs:
        raise ValueError("No data files found for the given period")

    all_data = pd.concat(dfs)
    all_data['thermal_stress'] = all_data['sea_surface_temperature_anomaly'] - threshold
    all_data.loc[all_data['thermal_stress'] < 0, 'thermal_stress'] = 0

    dhw_df = (
        all_data.groupby(['latitude', 'longitude'])
        ['thermal_stress']
        .sum()
        .reset_index()
    )
    dhw_df['DHW'] = dhw_df['thermal_stress'] / 7
    dhw_df.drop(columns=['thermal_stress'], inplace=True)

    dhw_df['time'] = end_date.strftime('%Y-%m-%dT12:00:00Z')
    dhw_df = dhw_df[['time', 'latitude', 'longitude', 'DHW']]

    return dhw_df

if __name__ == "__main__":
    # Put your actual project root path here:
    project_root = r"C:\Users\AdrienSourdille\Coral_Bleaching_Live_Map"

    dhw = load_and_calculate_dhw(project_root)
    output_folder = os.path.join(project_root, "data", "base")
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, "dhw_12weeks.csv")
    dhw.to_csv(output_path, index=False)
    print(f"DHW calculation complete and saved to {output_path}")

