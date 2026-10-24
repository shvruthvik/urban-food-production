
import pandas as pd
from pathlib import Path

# Project folders
project_folder = Path(__file__).resolve().parents[2]

health_raw_folder = project_folder / "data" / "raw" / "health"
integrated_folder = project_folder / "data" / "processed" / "integrated"
health_output_folder = project_folder / "data" / "processed" / "health"

health_output_folder.mkdir(parents=True, exist_ok=True)

places_file = (
    health_raw_folder
    / "PLACES__Census_Tract_Data_(GIS_Friendly_Format),_2023_release_20260112.csv"
)

kc_file = integrated_folder / "kc_metro_tract_data.csv"

# Read the KC metro health data already filtered to 516 tracts
kc = pd.read_csv(kc_file, dtype={"TractFIPS": str})

# Read column names from the original PLACES file
columns = pd.read_csv(places_file, nrows=0).columns.tolist()

# Identify candidate prevalence measures
health_vars = [
    col for col in columns
    if col.endswith("_CrudePrev")
]

print("Number of crude prevalence measures:", len(health_vars))
print("\nAvailable measures:")
for variable in health_vars:
    print(variable)

# Check data quality in the KC metro dataset
quality = []

for variable in health_vars:
    if variable not in kc.columns:
        continue

    values = pd.to_numeric(kc[variable], errors="coerce")

    quality.append({
        "Variable": variable,
        "Missing_Count": values.isna().sum(),
        "Missing_Percent": round(values.isna().mean() * 100, 2),
        "Valid_Count": values.notna().sum(),
        "Minimum": values.min(),
        "Maximum": values.max(),
        "Mean": values.mean(),
        "Standard_Deviation": values.std()
    })

quality_df = pd.DataFrame(quality)

quality_df.to_csv(
    health_output_folder / "health_variable_quality.csv",
    index=False
)

print("\nHealth variable quality summary:")
print(quality_df.to_string(index=False))

# Correlations between candidate measures
candidate_columns = quality_df["Variable"].tolist()

correlations = kc[candidate_columns].corr()

correlations.to_csv(
    health_output_folder / "health_variable_correlations.csv"
)

print("\nSaved quality and correlation files.")
