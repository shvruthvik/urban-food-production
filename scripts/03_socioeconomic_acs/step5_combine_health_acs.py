
import pandas as pd
from pathlib import Path

# Set the project and data folders
project_folder = Path(__file__).resolve().parents[2]

health_file = (
    project_folder / "data" / "processed" / "integrated"
    / "kc_metro_tract_data.csv"
)

acs_file = (
    project_folder / "data" / "raw" / "socioeconomic"
    / "acs_2019_kc_metro_cleaned.csv"
)

output_folder = (
    project_folder / "data" / "processed" / "integrated"
)
output_folder.mkdir(parents=True, exist_ok=True)

# Load the existing datasets
health = pd.read_csv(health_file, dtype={"TractFIPS": str})
acs = pd.read_csv(acs_file, dtype={"GEOID": str})

# Remove any accidental spaces and standardize tract IDs
health["TractFIPS"] = health["TractFIPS"].str.strip().str.zfill(11)
acs["GEOID"] = acs["GEOID"].str.strip().str.zfill(11)

# Check the original datasets
print("Health rows:", len(health))
print("Unique health tracts:", health["TractFIPS"].nunique())
print("ACS rows:", len(acs))
print("Unique ACS tracts:", acs["GEOID"].nunique())

# Keep only the ACS columns needed for analysis
acs_columns = [
    "GEOID",
    "Poverty_Percent",
    "Foreign_Born_Percent",
    "No_Vehicle_Households_Percent",
    "SNAP_Households_Percent",
    "Non_Hispanic_Black_Percent",
    "Hispanic_Latino_Percent",
    "Households_With_Children_Percent",
    "Renter_Occupied_Percent",
    "Bachelors_Or_Higher_Percent",
    "Age_65_Plus_Percent",
    "B19013_001E",
    "B25064_001E",
    "B25077_001E"
]

acs_selected = acs[acs_columns].copy()

# Merge using the census tract ID
combined = health.merge(
    acs_selected,
    left_on="TractFIPS",
    right_on="GEOID",
    how="left",
    validate="one_to_one",
    indicator=True
)

# Check the merge results
print("\nMerge results:")
print(combined["_merge"].value_counts())

print("\nCombined rows:", len(combined))
print("Unique combined tracts:", combined["TractFIPS"].nunique())

# Check health indicators
health_columns = [
    "OBESITY_CrudePrev",
    "DIABETES_CrudePrev",
    "BPHIGH_CrudePrev"
]

print("\nMissing health values:")
print(combined[health_columns].isna().sum())

print("\nMissing ACS values:")
print(combined[acs_columns[1:]].isna().sum())

# Remove merge-checking columns
combined = combined.drop(columns=["GEOID", "_merge"])

# Save as a new file
output_file = (
    output_folder / "kc_metro_combined_health_socioeconomic.csv"
)
combined.to_csv(output_file, index=False)

print("\nSaved combined dataset to:", output_file)


# Check unmatched IDs in the original health and ACS datasets

health_ids = set(health["TractFIPS"])
acs_ids = set(acs["GEOID"])

print("\nHEALTH VS. ACS ID CHECK")
print("Health IDs:", len(health_ids))
print("ACS IDs:", len(acs_ids))
print("IDs found in both:", len(health_ids & acs_ids))
print("Health IDs missing from ACS:", len(health_ids - acs_ids))
print("ACS IDs missing from health:", len(acs_ids - health_ids))

print("\nExamples of health IDs missing from ACS:")
print(sorted(health_ids - acs_ids)[:10])
