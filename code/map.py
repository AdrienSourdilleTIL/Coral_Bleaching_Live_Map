#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Resolve project root
project_root = Path(__file__).resolve().parents[1]
print(f"Using project root: {project_root}")

# Define paths
shapefile_gbr_zone = project_root / "data" / "raw" / "shapefile_gbr" / "worldheritagemarineprogramme.shp"
shapefile_gbr_features = project_root / "data" / "raw" / "shapefile" / "Great_Barrier_Reef_Features.shp"
csv_path = project_root / "data" / "base" / "dhw_12weeks.csv"
output_path = project_root / "output" / "dhw_map.png"

# Load GBR zone and features
gbr_zone = gpd.read_file(shapefile_gbr_zone).to_crs("EPSG:4326")
gbr_features = gpd.read_file(shapefile_gbr_features).to_crs("EPSG:4326")

# Load SST anomaly data
sst_df = pd.read_csv(csv_path, skiprows=[1])

# Convert to GeoDataFrame
sst_gdf = gpd.GeoDataFrame(
    sst_df,
    geometry=gpd.points_from_xy(sst_df['longitude'], sst_df['latitude']),
    crs="EPSG:4326"
)

# Filter points within GBR zone
sst_in_gbr = gpd.sjoin(sst_gdf, gbr_zone, predicate='within', how='inner')

# Compute average DHW inside GBR zone
mean_dhw = sst_in_gbr['DHW'].mean()
print(f"Average DHW inside GBR zone: {mean_dhw:.2f}°C·weeks")

# Current date
current_date = datetime.now().strftime("%Y-%m-%d")

# Plot all DHW points (unfiltered)
fig, ax = plt.subplots(figsize=(10, 8))
sst_gdf.plot(
    ax=ax,
    column='DHW',
    cmap='hot_r',
    legend=True,
    markersize=10,
    alpha=0.7,
    vmax=10
)

# Plot GBR features boundary (thin black line)
gbr_features.boundary.plot(ax=ax, color='black', linewidth=0.1)

# Titles and labels
ax.set_title(
    f"12-Week Cumulative Heat Stress (DHW) – {current_date}\nAvg DHW in the GBR zone: {mean_dhw:.2f}°C·weeks",
    fontsize=13
)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

plt.tight_layout()
plt.show()

# Export
fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Map saved to: {output_path}")
