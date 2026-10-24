
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "raw" / "socioeconomic"

input_file = data_folder / "acs_2019_candidate_diagnostic.csv"
output_file = data_folder / "acs_2019_kc_metro_cleaned.csv"

df = pd.read_csv(input_file, dtype={"GEOID": str})

# Convert ACS estimate columns to numeric
estimate_columns = [
    column for column in df.columns
    if column.endswith("E")
]

for column in estimate_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Replace Census sentinel values with missing values
df[estimate_columns] = df[estimate_columns].replace(
    -666666666, float("nan")
)

# Create a readable label for each tract
df["TractLabel"] = (
    df["StateDesc"].fillna("")
    + " - "
    + df["CountyName"].fillna("")
    + " - "
    + df["GEOID"].fillna("")
)

# Recalculate percentages after cleaning the estimates
def safe_percent(numerator, denominator):
    denominator = denominator.where(denominator > 0)
    return numerator.div(denominator) * 100

df["Poverty_Percent"] = safe_percent(
    df["B17001_002E"], df["B17001_001E"]
)

df["Foreign_Born_Percent"] = safe_percent(
    df["B05002_013E"], df["B05002_001E"]
)

df["No_Vehicle_Households_Percent"] = safe_percent(
    df["B08201_002E"], df["B08201_001E"]
)

df["SNAP_Households_Percent"] = safe_percent(
    df["B22003_002E"], df["B22003_001E"]
)

df["Non_Hispanic_Black_Percent"] = safe_percent(
    df["B03002_004E"], df["B03002_001E"]
)

df["Hispanic_Latino_Percent"] = safe_percent(
    df["B03002_012E"], df["B03002_001E"]
)

df["Households_With_Children_Percent"] = safe_percent(
    df["B11005_002E"], df["B11005_001E"]
)

df["Renter_Occupied_Percent"] = safe_percent(
    df["B25003_003E"], df["B25003_001E"]
)

education_columns = [
    "B15003_022E",
    "B15003_023E",
    "B15003_024E",
    "B15003_025E"
]

education_total = df[education_columns].sum(
    axis=1, min_count=1
)

df["Bachelors_Or_Higher_Percent"] = safe_percent(
    education_total, df["B15003_001E"]
)

age_columns = [
    "B01001_020E", "B01001_021E", "B01001_022E",
    "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E"
]

age_65_plus = df[age_columns].sum(axis=1, min_count=1)

df["Age_65_Plus_Percent"] = safe_percent(
    age_65_plus, df["B01001_001E"]
)

# Check the cleaned data
print("Rows:", len(df))
print("Unique GEOIDs:", df["GEOID"].nunique())

print("\nRemaining negative values in median estimates:")
for column in [
    "B19013_001E",
    "B25064_001E",
    "B25077_001E"
]:
    print(column, ":", (df[column] < 0).sum())

percentage_columns = [
    "Poverty_Percent",
    "Foreign_Born_Percent",
    "No_Vehicle_Households_Percent",
    "SNAP_Households_Percent",
    "Bachelors_Or_Higher_Percent",
    "Age_65_Plus_Percent"
]

print("\nMissing percentages:")
print(df[percentage_columns].isna().sum().to_string())

print("\nCleaned percentage summaries:")
print(df[percentage_columns].describe().round(2).to_string())

# Save the cleaned dataset
df.to_csv(output_file, index=False)

print("\nCleaned dataset saved to:")
print(output_file)
