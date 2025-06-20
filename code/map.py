#!/usr/bin/env python
# coding: utf-8

from pathlib import Path
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx

# Resolve project root
project_root = Path(__file__).resolve().parents[1]
print(f"Using project root: {project_root}")

# Define paths
shapefile_gbr = project_root / "data" / "raw" / "shapefile_gbr" / "worldheritagemarineprogramme.shp"
shapefile_gbr_features = project_root / "data" / "raw" / "shapefile_gbr" / "Great_Barrier_Reef_Features.shp"
csv_path = project_root / "data" / "base" / "dhw_12weeks.csv"
output_path = project_root / "output" / "dhw_map.png"

# Load GBR shapefile
gbr = gpd.read_file(shapefile_gbr).to_crs("EPSG:4326")

# Load GBR features
gbr_features = gpd.read_file(shapefile_gbr_features).to_crs("EPSG:4326")

# Load SST anomaly data
sst_df = pd.read_csv(csv_path, skiprows=[1])

# Convert to GeoDataFrame
sst_gdf = gpd.GeoDataFrame(
    sst_df,
    geometry=gpd.points_from_xy(sst_df['longitude'], sst_df['latitude']),
    crs="EPSG:4326"
)

# Spatial join: keep only points within GBR polygon
sst_within_gbr = gpd.sjoin(sst_gdf, gbr, predicate='within', how='inner')

# Compute average DHW
mean_dhw = sst_within_gbr['DHW'].mean()
print(f"Average DHW inside GBR: {mean_dhw:.2f}°C·weeks")

# Plot DHW points
fig, ax = plt.subplots(figsize=(10, 8))

# Plot DHW points inside GBR
sst_within_gbr.plot(
    ax=ax,
    column='DHW',
    cmap='hot_r',
    legend=True,
    markersize=10,
    alpha=0.7
)

# Outline GBR region and features
gbr.boundary.plot(ax=ax, color='black', linewidth=1)
gbr_features.boundary.plot(ax=ax, color='blue', linewidth=0.8, linestyle='--')

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=sst_gdf.crs)

# Titles and labels
ax.set_title(f"12-Week Cumulative Heat Stress (DHW) – Great Barrier Reef\nAvg DHW: {mean_dhw:.2f}°C·weeks", fontsize=13)
ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")

plt.tight_layout()
plt.show()

# Export
fig.savefig(output_path, dpi=300, bbox_inches='tight')
print(f"Map saved to: {output_path}")
