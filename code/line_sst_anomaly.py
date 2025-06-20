#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path
from shapely.geometry import Point

# Paths
daily_data_root = Path(r"C:\Users\AdrienSourdille\Coral_Bleaching_Live_Map\data\raw\daily")
gbr_shapefile_path = r"C:\Users\AdrienSourdille\Coral_Bleaching_Live_Map\data\raw\shapefile_gbr\worldheritagemarineprogramme.shp"
output_plot_path = r"C:\Users\AdrienSourdille\Coral_Bleaching_Live_Map\output\sst_anomaly_timeseries.png"

# Load GBR polygon
gbr_gdf = gpd.read_file(gbr_shapefile_path).to_crs("EPSG:4326")

# Load and combine all daily CSVs
csv_files = list(daily_data_root.rglob("sst_anomaly_*.csv"))
records = []

for csv_file in csv_files:
    df = pd.read_csv(
        csv_file,
        usecols=["longitude", "latitude", "time", "sea_surface_temperature_anomaly"],
        skiprows=[1]
    )
    df.dropna(subset=["longitude", "latitude", "time", "sea_surface_temperature_anomaly"], inplace=True)
    records.append(df)

all_data = pd.concat(records, ignore_index=True)
all_data['time'] = pd.to_datetime(all_data['time'])

# Convert to GeoDataFrame
geometry = gpd.points_from_xy(all_data.longitude, all_data.latitude)
gdf_all = gpd.GeoDataFrame(all_data, geometry=geometry, crs="EPSG:4326")

# Spatial filter: keep only points inside GBR polygon
gdf_filtered = gdf_all[gdf_all.within(gbr_gdf.unary_union)]

# Group by date and compute mean anomaly
daily_avg = gdf_filtered.groupby(gdf_filtered['time'].dt.date)['sea_surface_temperature_anomaly'].mean().reset_index()
daily_avg.columns = ['Date', 'Avg_SST_Anomaly']

# Plot the time series
plt.figure(figsize=(12, 6))
plt.plot(daily_avg['Date'], daily_avg['Avg_SST_Anomaly'], label='Avg SST Anomaly', color='tomato')
plt.axhline(0, color='gray', linestyle='--', linewidth=1)
plt.xlabel('Date')
plt.ylabel('SST Anomaly (°C)')
plt.title('Daily Average Sea Surface Temperature Anomaly in the GBR')
plt.grid(True)
plt.tight_layout()
plt.savefig(output_plot_path)
plt.close()

