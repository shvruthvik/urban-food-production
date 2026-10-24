
from pathlib import Path
import pandas as pd

folder = Path("data/tract_boundaries")

files = [
    folder / "tab20_tract20_tract10_st20.txt",
    folder / "tab20_tract20_tract10_st29.txt"
]

output_folder = Path("data")

study_counties = {
    ("20", "091"), ("20", "103"), ("20", "107"),
    ("20", "121"), ("20", "209"),
    ("29", "013"), ("29", "025"), ("29", "037"),
    ("29", "047"), ("29", "049"), ("29", "095"),
    ("29", "107"), ("29", "165"), ("29", "177")
}

# Read both original Census relationship files
frames = []

for file in files:
    if not file.exists():
        raise FileNotFoundError(f"Missing file: {file}")

    frames.append(pd.read_csv(file, sep="|", dtype=str))

all_links = pd.concat(frames, ignore_index=True)

# Clean the tract IDs
for column in ["GEOID_TRACT_20", "GEOID_TRACT_10"]:
    all_links[column] = (
        all_links[column].astype(str).str.strip().str.zfill(11)
    )

# Identify 2020 tracts inside the study counties
all_links["STATEFP20"] = all_links["GEOID_TRACT_20"].str[:2]
all_links["COUNTYFP20"] = all_links["GEOID_TRACT_20"].str[2:5]

inside = all_links[
    all_links.apply(
        lambda row: (
            row["STATEFP20"], row["COUNTYFP20"]
        ) in study_counties,
        axis=1
    )
].copy()

# Find all 2010 tracts linked to study-area 2020 tracts
relevant_2010_ids = set(inside["GEOID_TRACT_10"])

# Retain ALL relationships for those 2010 tracts,
# including relationships to 2020 tracts outside the study area
complete = all_links[
    all_links["GEOID_TRACT_10"].isin(relevant_2010_ids)
].copy()

# Summarize land overlap for each 2010/2020 tract pair
complete["AREALAND_PART"] = pd.to_numeric(
    complete["AREALAND_PART"],
    errors="coerce"
)

crosswalk = (
    complete.dropna(
        subset=[
            "GEOID_TRACT_10",
            "GEOID_TRACT_20",
            "AREALAND_PART"
        ]
    )
    .groupby(
        ["GEOID_TRACT_10", "GEOID_TRACT_20"],
        as_index=False
    )
    .agg(Land_Area_Overlap=("AREALAND_PART", "sum"))
)

# Calculate shares using ALL retained relationships
crosswalk["Old_Tract_Overlap_Total"] = (
    crosswalk.groupby("GEOID_TRACT_10")[
        "Land_Area_Overlap"
    ].transform("sum")
)

crosswalk["Share_of_Old_Tract_Overlap"] = (
    crosswalk["Land_Area_Overlap"]
    / crosswalk["Old_Tract_Overlap_Total"]
)

# Save as a new file; do not overwrite the original
output_file = output_folder / "kc_metro_2010_2020_tract_relationships_complete.csv"
crosswalk.to_csv(output_file, index=False)

# Verify the shares sum to 1 for each old tract
share_totals = crosswalk.groupby(
    "GEOID_TRACT_10"
)["Share_of_Old_Tract_Overlap"].sum()

print("COMPLETE CROSSWALK SUMMARY")
print("=" * 45)
print("Relevant 2010 tracts:", crosswalk["GEOID_TRACT_10"].nunique())
print("Related 2020 tracts:", crosswalk["GEOID_TRACT_20"].nunique())
print("Relationship pairs:", len(crosswalk))
print("2010 tracts with shares not approximately 1:",
      int(((share_totals - 1).abs() > 0.001).sum()))
print("Saved:", output_file)
