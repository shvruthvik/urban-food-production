
import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
data_folder = folder / "data"

crosswalk_file = data_folder / "kc_metro_2010_2020_tract_relationships_complete.csv"
audit_file = data_folder / "sram_unmatched_tract_audit.csv"

crosswalk = pd.read_csv(crosswalk_file, dtype={"GEOID_TRACT_10": str, "GEOID_TRACT_20": str})
audit = pd.read_csv(audit_file, dtype={"GEOID": str})

# Keep only the 86 unmatched project tracts
tract_ids = set(audit["GEOID"])
data = crosswalk[crosswalk["GEOID_TRACT_10"].isin(tract_ids)].copy()

data["Share_of_Old_Tract_Overlap"] = pd.to_numeric(
    data["Share_of_Old_Tract_Overlap"], errors="coerce"
)

# Find the largest overlap share for each old tract
summary = (
    data.groupby("GEOID_TRACT_10")
    .agg(
        Related_2020_Tracts=("GEOID_TRACT_20", "nunique"),
        Largest_Overlap_Share=("Share_of_Old_Tract_Overlap", "max"),
        Total_Overlap_Share=("Share_of_Old_Tract_Overlap", "sum")
    )
    .reset_index()
)

summary["Largest_Overlap_Percent"] = (
    summary["Largest_Overlap_Share"] * 100
).round(2)

summary["Total_Overlap_Percent"] = (
    summary["Total_Overlap_Share"] * 100
).round(2)

summary = summary.sort_values(
    ["Related_2020_Tracts", "Largest_Overlap_Share"],
    ascending=[False, False]
)

output_file = data_folder / "sram_unmatched_overlap_summary.csv"
summary.to_csv(output_file, index=False)

print("=" * 55)
print("UNMATCHED TRACT OVERLAP SUMMARY")
print("=" * 55)
print(f"Tracts summarized: {len(summary)}")
print("\nLargest overlap share across the 86 tracts:")
print(summary["Largest_Overlap_Percent"].describe().round(2))

print("\nLargest overlap share categories:")
print(
    pd.cut(
        summary["Largest_Overlap_Percent"],
        bins=[-1, 50, 75, 90, 100.01],
        labels=["50% or less", "Over 50% to 75%", "Over 75% to 90%", "Over 90%"]
    )
    .value_counts(sort=False)
    .to_string()
)

print(f"\nDetailed results saved to:\n{output_file}")

print("\nFirst 15 rows:")
print(summary.head(15).to_string(index=False))
