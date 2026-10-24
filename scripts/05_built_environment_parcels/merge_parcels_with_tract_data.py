
from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "processed" / "integrated"
parcel_folder = project_folder / "outputs" / "parcels"

# Load the existing tract-level dataset and parcel counts
tracts = pd.read_csv(
    data_folder / "kc_metro_combined_health_socioeconomic_LRAM2019.csv",
    dtype={"TractFIPS": str}
)

parcel_counts = pd.read_csv(
    parcel_folder / "candidate_parcel_counts_by_tract.csv",
    dtype={"GEOID": str}
)

# Normalize census tract IDs to 11-character strings
tracts["TractFIPS"] = (
    tracts["TractFIPS"].str.replace(r"\.0$", "", regex=True).str.zfill(11)
)

parcel_counts["GEOID"] = (
    parcel_counts["GEOID"].str.replace(r"\.0$", "", regex=True).str.zfill(11)
)

print("Original tract records:", len(tracts))
print("Unique tract IDs:", tracts["TractFIPS"].nunique())
print("Tracts with parcel counts:", len(parcel_counts))
print("Unique parcel-count tract IDs:", parcel_counts["GEOID"].nunique())

# Make sure the parcel-count file has one row per tract
if parcel_counts["GEOID"].duplicated().any():
    raise ValueError("Duplicate GEOID values found in parcel-count file.")

# Match the parcel counts to the existing tract dataset
combined = tracts.merge(
    parcel_counts,
    left_on="TractFIPS",
    right_on="GEOID",
    how="left",
    validate="one_to_one"
)

# Tracts with no matching candidate parcels receive a count of zero
count_columns = [
    column for column in combined.columns
    if column.startswith("Code_") and column.endswith("_Count")
]

if "TotalCandidateParcels" in combined.columns:
    count_columns.append("TotalCandidateParcels")

combined[count_columns] = combined[count_columns].fillna(0)

# Remove the duplicate tract ID column from the output
combined = combined.drop(columns=["GEOID"])

output_file = (
    data_folder / "kc_metro_health_socioeconomic_parcel_counts.csv"
)
combined.to_csv(output_file, index=False)

print("\nMERGE VALIDATION")
print("Output rows:", len(combined))
print("Unique output tracts:", combined["TractFIPS"].nunique())
print(
    "Tracts with candidate parcels:",
    (combined["TotalCandidateParcels"] > 0).sum()
)
print(
    "Tracts with zero candidate parcels:",
    (combined["TotalCandidateParcels"] == 0).sum()
)
print(
    "Total assigned candidate parcels:",
    int(combined["TotalCandidateParcels"].sum())
)

print("\nSaved:", output_file)

