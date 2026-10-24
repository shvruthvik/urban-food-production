
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# STEP 1: File paths
# --------------------------------------------------

folder = Path("data/tract_boundaries")

files = [
    folder / "tab20_tract20_tract10_st20.txt",
    folder / "tab20_tract20_tract10_st29.txt"
]

output_folder = Path("data")
output_folder.mkdir(exist_ok=True)

# Our 14 Kansas City metro counties
study_counties = {
    ("20", "091"), ("20", "103"), ("20", "107"),
    ("20", "121"), ("20", "209"),
    ("29", "013"), ("29", "025"), ("29", "037"),
    ("29", "047"), ("29", "049"), ("29", "095"),
    ("29", "107"), ("29", "165"), ("29", "177")
}

# --------------------------------------------------
# STEP 2: Read both state files
# --------------------------------------------------

frames = []

for file in files:
    if not file.exists():
        raise FileNotFoundError(f"Missing file: {file}")

    df = pd.read_csv(file, sep="|", dtype=str)
    frames.append(df)

relationships = pd.concat(frames, ignore_index=True)

# --------------------------------------------------
# STEP 3: Clean tract IDs
# --------------------------------------------------

for column in ["GEOID_TRACT_20", "GEOID_TRACT_10"]:
    relationships[column] = (
        relationships[column].astype(str).str.strip().str.zfill(11)
    )

# Keep only relationships where the 2020 tract is
# inside one of our 14 study-area counties.
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
# STEP 4: Summarize the geographic relationships
# --------------------------------------------------

tract_2020_count = relationships["GEOID_TRACT_20"].nunique()
tract_2010_count = relationships["GEOID_TRACT_10"].nunique()

relationships_per_2020 = (
    relationships.groupby("GEOID_TRACT_20")["GEOID_TRACT_10"]
    .nunique()
)

relationships_per_2010 = (
    relationships.groupby("GEOID_TRACT_10")["GEOID_TRACT_20"]
    .nunique()
)

print("\nTRACT RELATIONSHIP ANALYSIS")
print("=" * 55)

print("Relationship rows in study counties:", len(relationships))
print("Unique 2020 tracts:", tract_2020_count)
print("Unique 2010 tracts:", tract_2010_count)

print("\nNumber of 2010 tracts overlapping each 2020 tract:")
print(relationships_per_2020.value_counts().sort_index())

print("\nNumber of 2020 tracts overlapping each 2010 tract:")
print(relationships_per_2010.value_counts().sort_index())

# --------------------------------------------------
# STEP 5: Identify tracts with multiple relationships
# --------------------------------------------------

multiple_2010 = relationships_per_2020[
    relationships_per_2020 > 1
]

multiple_2020 = relationships_per_2010[
    relationships_per_2010 > 1
]

print("\n2020 tracts linked to multiple 2010 tracts:",
      len(multiple_2010))

print("2010 tracts linked to multiple 2020 tracts:",
      len(multiple_2020))

# --------------------------------------------------
# STEP 6: Save the filtered relationship data
# --------------------------------------------------

relationship_output = (
    output_folder / "kc_metro_2010_2020_tract_relationships.csv"
)

relationships.to_csv(relationship_output, index=False)

summary = pd.DataFrame({
    "GEOID_TRACT_20": relationships_per_2020.index,
    "Number_of_2010_Tracts": relationships_per_2020.values
})

summary.to_csv(
    output_folder / "kc_metro_2020_tract_relationship_summary.csv",
    index=False
)

print("\nFiles saved:")
print(relationship_output)
print(output_folder / "kc_metro_2020_tract_relationship_summary.csv")
