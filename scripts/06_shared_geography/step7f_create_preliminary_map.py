
from pathlib import Path
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Set project folders
project_folder = Path.cwd()
data_folder = project_folder / "data"

# Find the 2019 boundary files
kansas_file = list(
    project_folder.rglob("tl_2019_20_tract.shp")
)[0]

missouri_file = list(
    project_folder.rglob("tl_2019_29_tract.shp")
)[0]

# Read the health and socioeconomic dataset
data = pd.read_csv(
    data_folder / "kc_metro_combined_health_socioeconomic.csv",
    dtype={"TractFIPS": str}
)

data["TractFIPS"] = data["TractFIPS"].str.strip()

# Read the Kansas and Missouri tract boundaries
kansas = gpd.read_file(kansas_file)
missouri = gpd.read_file(missouri_file)

kansas["GEOID"] = kansas["GEOID"].astype(str).str.strip()
missouri["GEOID"] = missouri["GEOID"].astype(str).str.strip()

# Combine the two states
boundaries = gpd.GeoDataFrame(
    pd.concat([kansas, missouri], ignore_index=True),
    geometry="geometry",
    crs=kansas.crs
)

# Keep only boundaries for our study area
study_ids = set(data["TractFIPS"])
study_boundaries = boundaries[
    boundaries["GEOID"].isin(study_ids)
].copy()

print("Study data rows:", len(data))
print("Matched polygons:", len(study_boundaries))
print("Unique matched IDs:", study_boundaries["GEOID"].nunique())

# Check the match before joining
if (
    len(data) != 516
    or len(study_boundaries) != 516
    or study_boundaries["GEOID"].nunique() != 516
):
    raise ValueError(
        "The expected 516 unique tract matches were not found."
    )

# Join health and socioeconomic data to the polygons
result = study_boundaries.merge(
    data,
    left_on="GEOID",
    right_on="TractFIPS",
    how="left",
    validate="one_to_one",
    indicator=True
)

print("Rows after join:", len(result))
print("Successful data matches:", (result["_merge"] == "both").sum())

if not (result["_merge"] == "both").all():
    raise ValueError("Some polygons did not receive study data.")

result = result.drop(columns=["_merge"])

# Save the joined geographic dataset
geojson_path = data_folder / "kc_metro_tracts_with_data.geojson"
result.to_file(geojson_path, driver="GeoJSON")
print("Saved geographic dataset:", geojson_path)

# Reproject for a regional map
map_data = result.to_crs(epsg=5070)

# Draw the preliminary tract boundary map
fig, ax = plt.subplots(figsize=(12, 10))

map_data.plot(
    ax=ax,
    facecolor="lightgray",
    edgecolor="black",
    linewidth=0.25
)

ax.set_title(
    "Kansas City Metro Study Area\n"
    "Census Tract Boundaries (2019)",
    fontsize=16
)
ax.set_axis_off()

plt.tight_layout()

map_path = data_folder / "kc_metro_tract_boundaries_map.png"
plt.savefig(map_path, dpi=300, bbox_inches="tight")
plt.close()

print("Saved preliminary map:", map_path)
print("\nPreliminary map creation complete.")
