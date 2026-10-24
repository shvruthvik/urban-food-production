
import pandas as pd
import geopandas as gpd

# Load the existing project data.
project = pd.read_csv(
    "data/kc_metro_combined_health_socioeconomic.csv",
    dtype={"CountyFIPS": str, "TractFIPS": str}
)

# Construct the 11-digit census tract ID.
project["GEOID"] = (
    project["StateAbbr"].map({"KS": "20", "MO": "29"})
    + project["CountyFIPS"].str.zfill(3)
    + project["TractFIPS"].str.zfill(6)
)

# Load the existing tract map.
tract_map = gpd.read_file(
    "data/kc_metro_tracts_with_data.geojson"
)

# Load the USDA food-access data.
sram = pd.read_excel(
    "data/2025-sram-fara-data.xlsx",
    sheet_name="Driving Distance Data",
    header=1
)

print("PROJECT DATA")
print("Rows:", len(project))
print("Unique tract IDs:", project["GEOID"].nunique())
print("Sample tract IDs:", project["GEOID"].head().tolist())

print("\nPROJECT MAP")
print("Rows:", len(tract_map))
print("Geographic columns:", tract_map.columns.tolist())

print("\nUSDA SRAM DATA")
print("Rows:", len(sram))
print("Geographic columns:",
      sram[["CensusTract20", "State", "County20"]].columns.tolist())
print("Sample 2020 tract IDs:")
print(sram["CensusTract20"].head().tolist())

print("\nCheck complete.")
