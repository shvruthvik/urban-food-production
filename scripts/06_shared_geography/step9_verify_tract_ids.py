
import pandas as pd
import geopandas as gpd

# Load the existing map, which already contains GEOID.
tract_map = gpd.read_file(
    "data/kc_metro_tracts_with_data.geojson"
)

# Load the USDA driving-distance data.
sram = pd.read_excel(
    "data/2025-sram-fara-data.xlsx",
    sheet_name="Driving Distance Data",
    header=1,
    dtype={"CensusTract20": str}
)

# Normalize both IDs to strings and remove decimal artifacts.
project_ids = (
    tract_map["GEOID"]
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

sram_ids = (
    sram["CensusTract20"]
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

print("PROJECT GEOID EXAMPLES")
print(project_ids.head().tolist())
print("Project ID lengths:")
print(project_ids.str.len().value_counts().to_dict())

print("\nUSDA ID EXAMPLES")
print(sram_ids.head().tolist())
print("USDA ID lengths:")
print(sram_ids.str.len().value_counts().to_dict())

print("\nMATCH CHECK")
print("Project unique IDs:", project_ids.nunique())
print("USDA unique IDs:", sram_ids.nunique())
print("Exact ID matches:", project_ids.isin(set(sram_ids)).sum())

print("\nCheck complete.")
