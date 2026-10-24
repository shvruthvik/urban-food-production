
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "raw" / "socioeconomic"
file_path = data_folder / "acs_2019_kc_metro_candidate_data.csv"

df = pd.read_csv(file_path, dtype={"GEOID": str})

print("Total rows:", len(df))
print("Unique tracts:", df["GEOID"].nunique())

# Check missing values in every column
print("\nMissing values by column:")
missing = df.isna().sum()
print(missing[missing > 0].sort_values(ascending=False).to_string())

# Investigate the missing poverty percentage
print("\nTracts with missing poverty percentage:")
poverty_missing = df[df["Poverty_Percent"].isna()]

columns_to_show = [
    "GEOID",
    "NAME",
    "B17001_001E",
    "B17001_002E",
    "Poverty_Percent"
]

print(poverty_missing[columns_to_show].to_string(index=False))

# Check for negative values in ACS estimate columns
estimate_columns = [
    column for column in df.columns
    if column.endswith("E")
]

print("\nNegative ACS estimates by column:")
for column in estimate_columns:
    values = pd.to_numeric(df[column], errors="coerce")
    negative_count = (values < 0).sum()

    if negative_count > 0:
        print(column, ":", negative_count)

# Check percentage ranges
percentage_columns = [
    "Poverty_Percent",
    "Foreign_Born_Percent",
    "No_Vehicle_Households_Percent",
    "SNAP_Households_Percent",
    "Non_Hispanic_Black_Percent",
    "Hispanic_Latino_Percent",
    "Households_With_Children_Percent",
    "Renter_Occupied_Percent",
    "Bachelors_Or_Higher_Percent",
    "Age_65_Plus_Percent"
]

print("\nPercentage ranges:")
print(df[percentage_columns].describe().round(2).to_string())

# Save the audit report
report_path = data_folder / "acs_2019_audit_report.csv"

audit = pd.DataFrame({
    "Column": df.columns,
    "Missing_Count": [df[column].isna().sum() for column in df.columns]
})

audit.to_csv(report_path, index=False)

print("\nAudit report saved to:")
print(report_path)
