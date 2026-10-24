
from pathlib import Path
import pandas as pd

# Load the project tracts and crosswalk summary
health_file = Path("data/kc_metro_tract_data.csv")
crosswalk_file = Path("data/step12c_tract_crosswalk_summary.csv")

health = pd.read_csv(health_file, dtype=str)
crosswalk = pd.read_csv(crosswalk_file, dtype=str)

# Clean the tract IDs
health_ids = set(
    health["TractFIPS"].str.strip().str.zfill(11)
)

crosswalk["GEOID_TRACT_10"] = (
    crosswalk["GEOID_TRACT_10"].str.strip().str.zfill(11)
)

crosswalk["GEOID_TRACT_20"] = (
    crosswalk["GEOID_TRACT_20"].str.strip().str.zfill(11)
)

# Convert the area values to numbers
crosswalk["Land_Area_Overlap"] = pd.to_numeric(
    crosswalk["Land_Area_Overlap"], errors="coerce"
)

crosswalk["Old_Tract_Overlap_Total"] = pd.to_numeric(
    crosswalk["Old_Tract_Overlap_Total"], errors="coerce"
)

# Keep relationships for the 516 project tracts
project_crosswalk = crosswalk[
    crosswalk["GEOID_TRACT_10"].isin(health_ids)
].copy()

# Summarize how much recorded overlap area each tract has
coverage = (
    project_crosswalk.groupby("GEOID_TRACT_10")
    .agg(
        Related_2020_Tracts=("GEOID_TRACT_20", "nunique"),
        Recorded_Overlap=("Land_Area_Overlap", "sum"),
        Old_Tract_Total=("Old_Tract_Overlap_Total", "first")
    )
    .reset_index()
)

coverage["Coverage_Ratio"] = (
    coverage["Recorded_Overlap"] / coverage["Old_Tract_Total"]
)

# Check all 516 project tracts
coverage_ids = set(coverage["GEOID_TRACT_10"])
missing = sorted(health_ids - coverage_ids)

print("PROJECT CROSSWALK COVERAGE")
print("=" * 45)
print("Project tracts:", len(health_ids))
print("Tracts with crosswalk relationships:", len(coverage))
print("Tracts without crosswalk relationships:", len(missing))

print("\nCoverage ratio summary:")
print(coverage["Coverage_Ratio"].describe())

print("\nTracts with coverage below 99.9%:")
print(
    coverage.loc[
        coverage["Coverage_Ratio"] < 0.999,
        ["GEOID_TRACT_10", "Related_2020_Tracts", "Coverage_Ratio"]
    ].to_string(index=False)
)

print("\nProject tracts without crosswalk relationships:")
print(missing)
