
from pathlib import Path
import pandas as pd
import geopandas as gpd

# --------------------------------------------------
# STEP 1: Set file paths
# --------------------------------------------------

project_file = Path("data/kc_metro_tracts_with_data.geojson")

relationship_files = [
    Path("data/tract_boundaries/tab20_tract20_tract10_st20.txt"),
    Path("data/tract_boundaries/tab20_tract20_tract10_st29.txt")
]

output_folder = Path("data")
output_folder.mkdir(exist_ok=True)

# --------------------------------------------------
# STEP 2: Check that the files exist
# --------------------------------------------------

if not project_file.exists():
    raise FileNotFoundError(f"Project file not found: {project_file}")

for file in relationship_files:
    if not file.exists():
        raise FileNotFoundError(f"Relationship file not found: {file}")

# --------------------------------------------------
# STEP 3: Load project tract IDs
# --------------------------------------------------

project = gpd.read_file(project_file)

if "GEOID" not in project.columns:
    raise ValueError("GEOID column not found in project GeoJSON.")

project_ids = set(
    project["GEOID"]
    .dropna()
    .astype(str)
    .str.strip()
    .str.zfill(11)
)

# --------------------------------------------------
# STEP 4: Load both relationship files
# --------------------------------------------------

frames = []

for file in relationship_files:
    df = pd.read_csv(file, sep="|", dtype=str)
    frames.append(df)

relationships = pd.concat(frames, ignore_index=True)

# Clean the 2010 and 2020 GEOID fields
for column in ["GEOID_TRACT_10", "GEOID_TRACT_20"]:
    relationships[column] = (
        relationships[column]
        .astype(str)
        .str.strip()
        .str.zfill(11)
    )

# Keep relationships for the 14 study-area counties,
# based on the 2020 tract geography.
study_counties = {
    ("20", "091"), ("20", "103"), ("20", "107"),
    ("20", "121"), ("20", "209"),
    ("29", "013"), ("29", "025"), ("29", "037"),
    ("29", "047"), ("29", "049"), ("29", "095"),
    ("29", "107"), ("29", "165"), ("29", "177")
}

relationships["STATEFP"] = relationships["GEOID_TRACT_20"].str[:2]
relationships["COUNTYFP"] = relationships["GEOID_TRACT_20"].str[2:5]

relationships = relationships[
    relationships.apply(
        lambda row: (row["STATEFP"], row["COUNTYFP"])
        in study_counties,
        axis=1
    )
].copy()

# --------------------------------------------------
# STEP 5: Compare project IDs with 2010 tract IDs
# --------------------------------------------------

tract_2010_ids = set(
    relationships["GEOID_TRACT_10"].dropna().unique()
)

matching_ids = project_ids & tract_2010_ids
project_not_in_2010 = project_ids - tract_2010_ids
tract_2010_not_in_project = tract_2010_ids - project_ids

print("\nPROJECT GEOIDS VS 2010 TRACT GEOIDS")
print("=" * 55)

print("Unique project GEOIDs:", len(project_ids))
print("Unique 2010 tract GEOIDs:", len(tract_2010_ids))
print("Matching GEOIDs:", len(matching_ids))
print("Project GEOIDs not in 2010 list:", len(project_not_in_2010))
print("2010 GEOIDs not in project:", len(tract_2010_not_in_project))

if project_ids:
    print(
        "Percentage of project IDs matching:",
        round(len(matching_ids) / len(project_ids) * 100, 2),
        "%"
    )

# --------------------------------------------------
# STEP 6: Save detailed comparison
# --------------------------------------------------

all_ids = sorted(project_ids | tract_2010_ids)

comparison = pd.DataFrame({"GEOID": all_ids})
comparison["In_Project"] = comparison["GEOID"].isin(project_ids)
comparison["In_2010_Relationship_File"] = (
    comparison["GEOID"].isin(tract_2010_ids)
)

comparison.to_csv(
    output_folder / "step12b_project_vs_2010_ids.csv",
    index=False
)

print("\nSaved:")
print(output_folder / "step12b_project_vs_2010_ids.csv")
print("\nComparison complete.")
