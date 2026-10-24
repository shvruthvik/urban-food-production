
import pandas as pd
from pathlib import Path

# Project folder
folder = Path(__file__).parent
data_folder = folder / "data"

# Input files
unmatched_file = data_folder / "sram_project_unmatched_ids.csv"
crosswalk_file = data_folder / "kc_metro_2010_2020_tract_relationships_complete.csv"

# Read the files
unmatched = pd.read_csv(unmatched_file, dtype=str)
crosswalk = pd.read_csv(crosswalk_file, dtype=str)

# Remove extra spaces and standardize tract IDs
unmatched["GEOID"] = unmatched["GEOID"].str.strip()
crosswalk["GEOID_TRACT_10"] = crosswalk["GEOID_TRACT_10"].str.strip()
crosswalk["GEOID_TRACT_20"] = crosswalk["GEOID_TRACT_20"].str.strip()

# Keep crosswalk rows for the unmatched project tracts
matched_rows = crosswalk[
    crosswalk["GEOID_TRACT_10"].isin(unmatched["GEOID"])
].copy()

# Count unique related 2020 tracts for each project tract
counts = (
    matched_rows.groupby("GEOID_TRACT_10")["GEOID_TRACT_20"]
    .nunique()
    .reset_index(name="Related_2020_Tract_Count")
)

# Include every unmatched tract, including those with no crosswalk match
report = unmatched.merge(
    counts,
    left_on="GEOID",
    right_on="GEOID_TRACT_10",
    how="left"
)

report["Related_2020_Tract_Count"] = (
    report["Related_2020_Tract_Count"].fillna(0).astype(int)
)

# Classify the relationship pattern
def classify(count):
    if count == 0:
        return "No crosswalk relationship"
    elif count == 1:
        return "One related 2020 tract"
    else:
        return "Multiple related 2020 tracts"

report["Relationship_Pattern"] = report[
    "Related_2020_Tract_Count"
].apply(classify)

# Add the related 2020 tract IDs for inspection
related_ids = (
    matched_rows.groupby("GEOID_TRACT_10")["GEOID_TRACT_20"]
    .apply(lambda values: "; ".join(sorted(set(values))))
    .reset_index(name="Related_2020_Tract_IDs")
)

report = report.merge(
    related_ids,
    left_on="GEOID",
    right_on="GEOID_TRACT_10",
    how="left",
    suffixes=("", "_extra")
)

# Save the detailed report
output_file = data_folder / "sram_unmatched_tract_audit.csv"
report.to_csv(output_file, index=False)

# Print the summary
print("=" * 60)
print("UNMATCHED TRACT AUDIT")
print("=" * 60)
print(f"Unmatched project tracts: {len(unmatched)}")
print("\nRelationship pattern counts:")

print(
    report["Relationship_Pattern"]
    .value_counts()
    .to_string()
)

print(f"\nDetailed report saved to:\n{output_file}")

print("\nFirst 15 rows:")
print(
    report[
        [
            "GEOID",
            "Related_2020_Tract_Count",
            "Relationship_Pattern",
            "Related_2020_Tract_IDs"
        ]
    ].head(15).to_string(index=False)
)
