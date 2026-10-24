
from pathlib import Path
import pandas as pd

# --------------------------------------------------
# STEP 1: Set paths
# --------------------------------------------------

relationship_file = Path(
    "data/kc_metro_2010_2020_tract_relationships.csv"
)

output_folder = Path("data")

# --------------------------------------------------
# STEP 2: Load the relationship data
# --------------------------------------------------

if not relationship_file.exists():
    raise FileNotFoundError(
        f"File not found: {relationship_file}"
    )

df = pd.read_csv(
    relationship_file,
    dtype=str
)

print("Relationship rows:", len(df))
print("Columns:", list(df.columns))

# --------------------------------------------------
# STEP 3: Check required columns
# --------------------------------------------------

required_columns = [
    "GEOID_TRACT_10",
    "GEOID_TRACT_20",
    "AREALAND_PART"
]

for column in required_columns:
    if column not in df.columns:
        raise ValueError(
            f"Required column missing: {column}"
        )

# --------------------------------------------------
# STEP 4: Clean tract IDs and land area
# --------------------------------------------------

for column in ["GEOID_TRACT_10", "GEOID_TRACT_20"]:
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .str.zfill(11)
    )

df["AREALAND_PART"] = pd.to_numeric(
    df["AREALAND_PART"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "GEOID_TRACT_10",
        "GEOID_TRACT_20",
        "AREALAND_PART"
    ]
)

# --------------------------------------------------
# STEP 5: Count related tracts
# --------------------------------------------------

old_to_new = (
    df.groupby("GEOID_TRACT_10")["GEOID_TRACT_20"]
    .nunique()
)

new_to_old = (
    df.groupby("GEOID_TRACT_20")["GEOID_TRACT_10"]
    .nunique()
)

print("\nTRACT RELATIONSHIP SUMMARY")
print("=" * 50)

print("Unique 2010 tracts:", df["GEOID_TRACT_10"].nunique())
print("Unique 2020 tracts:", df["GEOID_TRACT_20"].nunique())

print(
    "2010 tracts linked to multiple 2020 tracts:",
    int((old_to_new > 1).sum())
)

print(
    "2020 tracts linked to multiple 2010 tracts:",
    int((new_to_old > 1).sum())
)

# --------------------------------------------------
# STEP 6: Summarize each relationship
# --------------------------------------------------

crosswalk = (
    df.groupby(
        ["GEOID_TRACT_10", "GEOID_TRACT_20"],
        as_index=False
    )
    .agg(
        Land_Area_Overlap=("AREALAND_PART", "sum")
    )
)

# For each 2010 tract, calculate the share of its
# recorded overlap area associated with each 2020 tract.
crosswalk["Old_Tract_Overlap_Total"] = (
    crosswalk.groupby("GEOID_TRACT_10")[
        "Land_Area_Overlap"
    ].transform("sum")
)

crosswalk["Share_of_Old_Tract_Overlap"] = (
    crosswalk["Land_Area_Overlap"]
    / crosswalk["Old_Tract_Overlap_Total"]
)

# Save the detailed relationship table
crosswalk.to_csv(
    output_folder / "step12c_tract_crosswalk_summary.csv",
    index=False
)

# --------------------------------------------------
# STEP 7: Save counts for each tract
# --------------------------------------------------

old_summary = old_to_new.rename(
    "Number_of_2020_Tracts"
).reset_index()

new_summary = new_to_old.rename(
    "Number_of_2010_Tracts"
).reset_index()

old_summary.to_csv(
    output_folder / "step12c_2010_tract_link_counts.csv",
    index=False
)

new_summary.to_csv(
    output_folder / "step12c_2020_tract_link_counts.csv",
    index=False
)

print("\nFiles saved:")
print("data/step12c_tract_crosswalk_summary.csv")
print("data/step12c_2010_tract_link_counts.csv")
print("data/step12c_2020_tract_link_counts.csv")

print("\nFirst 10 crosswalk rows:")
print(crosswalk.head(10).to_string(index=False))

print("\nCrosswalk inspection complete.")
