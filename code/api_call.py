#!/usr/bin/env python
# coding: utf-8

# In[1]:


import requests
from datetime import datetime, timedelta
import os

def fetch_sst_anomaly():
    # Use 2 days ago to ensure data availability
    date = datetime.utcnow().date() - timedelta(days=1)
    timestamp = date.strftime("%Y-%m-%dT12:00:00Z")

    dataset_id = "noaacrwsstanomalyDaily"
    variable = "sea_surface_temperature_anomaly"

    # Build ERDDAP URL
    url = (
        f"https://coastwatch.noaa.gov/erddap/griddap/{dataset_id}.csv?"
        f"{variable}%5B({timestamp}):1:({timestamp})%5D"
        f"%5B(-10.475):1:(-24.475)%5D"
        f"%5B(142.475):1:(154.025)%5D"
    )

    # Determine project root safely
    from pathlib import Path
    project_root = Path(__file__).resolve().parents[1] if '__file__' in globals() else Path.cwd()
    print(f"Project root: {project_root}")

    # Build folder path relative to project root
    folder_path = os.path.join(
        project_root, "data", "raw", "daily",
        str(date.year),
        f"{date.month:02d}",
        f"{date.day:02d}"
    )
    os.makedirs(folder_path, exist_ok=True)

    # Build filename
    filename = f"sst_anomaly_{date.strftime('%Y_%m_%d')}.csv"
    output_path = os.path.join(folder_path, filename)
    print(f"Attempting to save file to: {output_path}")

    print(f"Fetching SST anomaly for {date} from NOAA ERDDAP...")
    response = requests.get(url)
    response.raise_for_status()

    with open(output_path, "wb") as f:
        f.write(response.content)

    print(f"Saved to: {output_path}")

if __name__ == "__main__":
    fetch_sst_anomaly()

