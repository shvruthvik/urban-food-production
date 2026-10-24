
import pandas as pd
from pathlib import Path

# Load the corrected crosswalk
crosswalk_file = Path(
    "data/kc_metro_2010_2020_tract_relationships_complete.csv"
)

if not crosswalk_file.exists():
    raise FileNotFoundError(f"File not found: {crosswalk_file}")

crosswalk = pd.read_csv(
    crosswalk_file,
    dtype={
        "GEOID_TRACT_10": str,
        "GEOID_TRACT_20": str
    }
)

# The first unmatched project tract
tract_id = "20091051804"

# Find all related 2020 tracts
related = crosswalk[
    crosswalk["GEOID_TRACT_10"] == tract_id
].copy()

print("CROSSWALK INSPECTION")
print("=" * 55)
print("Project tract:", tract_id)
print("Related 2020 tracts:", len(related))

if related.empty:
    print("No relationships found for this tract.")
else:
    print(
        related[
            [
                "GEOID_TRACT_10",
                "GEOID_TRACT_20",
                "Land_Area_Overlap",
                "Share_of_Old_Tract_Overlap"
            ]
        ].to_string(index=False)
    )

    print("\nShare total:",
          related["Share_of_Old_Tract_Overlap"].sum())

print("\nInspection complete.")
