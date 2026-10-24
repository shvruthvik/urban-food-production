
import pandas as pd
from pathlib import Path

# Load the combined dataset
project_folder = Path(__file__).resolve().parents[2]

data_folder = project_folder / "data" / "processed" / "integrated"

file_path = data_folder / "kc_metro_combined_health_socioeconomic.csv"

data = pd.read_csv(file_path, dtype={"TractFIPS": str})

# Check dataset size and tract IDs
print("Rows:", len(data))
print("Unique tracts:", data["TractFIPS"].nunique())
print("Duplicate tract IDs:", data["TractFIPS"].duplicated().sum())

# Check the health indicators
health_columns = [
    "OBESITY_CrudePrev",
    "DIABETES_CrudePrev",
    "BPHIGH_CrudePrev"
]

print("\nHealth indicator summary:")
print(data[health_columns].describe().round(2))

# Check the socioeconomic indicators
acs_columns = [
    "Poverty_Percent",
    "No_Vehicle_Households_Percent",
    "SNAP_Households_Percent",
    "B19013_001E",
    "B25064_001E",
    "B25077_001E"
]

print("\nSocioeconomic indicator summary:")
print(data[acs_columns].describe().round(2))

# Save missing-value counts
missing_values = data.isna().sum()
missing_values = missing_values[missing_values > 0]

print("\nColumns with missing values:")
print(missing_values)

missing_values.to_csv(
    data_folder / "kc_metro_combined_missing_values.csv",
    header=["Missing_Count"]
)

print("\nValidation complete.")
