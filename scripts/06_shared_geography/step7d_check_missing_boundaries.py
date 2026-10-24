
from pathlib import Path
import pandas as pd
import geopandas as gpd

data_folder = Path("data")
boundary_folder = data_folder / "tract_boundaries"

# Read the study data
data = pd.read_csv(
    data_folder / "kc_metro_combined_health_socioeconomic.csv",
    dtype=str
)
data["TractFIPS"] = data["TractFIPS"].str.strip()

# Read both boundary files
kansas = gpd.read_file(
    boundary_folder / "kansas" / "tl_2023_20_tract.shp"
)
missouri = gpd.read_file(
    boundary_folder / "missouri" / "tl_2023_29_tract.shp"
)

# Make sure the IDs have the same text format
kansas["GEOID"] = kansas["GEOID"].astype(str).str.strip()
missouri["GEOID"] = missouri["GEOID"].astype(str).str.strip()

# Check matches separately for each state
for state, boundary in [("Kansas", kansas), ("Missouri", missouri)]:
    study = data[data["StateDesc"].str.strip() == state]
    boundary_ids = set(boundary["GEOID"])
    study_ids = set(study["TractFIPS"])

    missing = sorted(study_ids - boundary_ids)

    print("\n", state)
    print("Study tracts:", len(study_ids))
    print("Matched:", len(study_ids & boundary_ids))
    print("Missing:", len(missing))
    print("First 20 missing IDs:", missing[:20])

# Check whether the missing IDs exist in either state file
all_boundary_ids = set(kansas["GEOID"]) | set(missouri["GEOID"])
all_missing = sorted(set(data["TractFIPS"]) - all_boundary_ids)

print("\nTotal unmatched IDs:", len(all_missing))
print("First 30 unmatched IDs:", all_missing[:30])
