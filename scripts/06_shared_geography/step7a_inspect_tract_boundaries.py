
from pathlib import Path
import pandas as pd
import geopandas as gpd

# Project folders
data_folder = Path("data")
boundary_folder = data_folder / "tract_boundaries"

# Our existing dataset with health and socioeconomic data
csv_path = data_folder / "kc_metro_combined_health_socioeconomic.csv"

# Read the combined dataset
data = pd.read_csv(csv_path, dtype=str)

print("COMBINED DATASET")
print("Number of rows:", len(data))
print("Column names:")
print(data.columns.tolist())

# Inspect the Kansas and Missouri boundary files
shapefiles = [
    boundary_folder / "kansas" / "tl_2023_20_tract.shp",
    boundary_folder / "missouri" / "tl_2023_29_tract.shp"
]

for shapefile in shapefiles:
    print("\n" + "=" * 50)
    print("FILE:", shapefile.name)

    tracts = gpd.read_file(shapefile)

    print("Number of polygons:", len(tracts))
    print("Coordinate system:", tracts.crs)
    print("Column names:")
    print(tracts.columns.tolist())

    # GEOID is the standard tract identifier in these files
    if "GEOID" in tracts.columns:
        print("Sample GEOIDs:")
        print(tracts["GEOID"].head().tolist())

print("\nInspection complete.")
