
from pathlib import Path
import pandas as pd
import geopandas as gpd

data_folder = Path("data")
boundary_folder = data_folder / "tract_boundaries"

# Read our combined health and socioeconomic dataset
data = pd.read_csv(
    data_folder / "kc_metro_combined_health_socioeconomic.csv",
    dtype=str
)

# Make sure tract identifiers have no extra spaces
data["TractFIPS"] = data["TractFIPS"].str.strip()

# Read Kansas and Missouri tract polygons
kansas = gpd.read_file(
    boundary_folder / "kansas" / "tl_2023_20_tract.shp"
)

missouri = gpd.read_file(
    boundary_folder / "missouri" / "tl_2023_29_tract.shp"
)

# Combine both states into one geographic dataset
boundaries = pd.concat(
    [kansas, missouri],
    ignore_index=True
)
boundaries = gpd.GeoDataFrame(
    boundaries,
    geometry="geometry",
    crs=kansas.crs
)

# Keep only the tracts in our study dataset
study_ids = set(data["TractFIPS"])
study_boundaries = boundaries[
    boundaries["GEOID"].isin(study_ids)
].copy()

# Check the geographic join
matched_ids = set(study_boundaries["GEOID"])
missing_ids = study_ids - matched_ids

print("Study dataset rows:", len(data))
print("Matched boundary polygons:", len(study_boundaries))
print("Unique matched GEOIDs:", study_boundaries["GEOID"].nunique())
print("Study IDs without boundaries:", len(missing_ids))

if missing_ids:
    print("Examples of missing IDs:", sorted(missing_ids)[:10])

# Check for duplicate boundary matches
print(
    "Duplicate GEOIDs in matched boundaries:",
    study_boundaries["GEOID"].duplicated().sum()
)

# Save a GIS-ready file only if all matches are valid
if (
    len(data) == 516
    and len(study_boundaries) == 516
    and study_boundaries["GEOID"].nunique() == 516
    and not missing_ids
):
    # Add the health and socioeconomic attributes
    result = study_boundaries.merge(
        data,
        left_on="GEOID",
        right_on="TractFIPS",
        how="left",
        validate="one_to_one"
    )

    output_path = data_folder / "kc_metro_tracts_with_data.geojson"
    result.to_file(output_path, driver="GeoJSON")

    print("\nJoin successful.")
    print("Saved:", output_path)
else:
    print("\nJoin not saved. Review the matching results first.")

