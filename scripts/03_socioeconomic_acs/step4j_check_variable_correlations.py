
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "raw" / "socioeconomic"
file_path = data_folder / "acs_2019_kc_metro_cleaned.csv"

df = pd.read_csv(file_path, dtype={"GEOID": str})

candidate_columns = [
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

# Keep only candidate columns that exist in the file
candidate_columns = [
    column for column in candidate_columns
    if column in df.columns
]

# Convert the selected variables to numeric
for column in candidate_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Calculate correlations between candidate variables
correlation_matrix = df[candidate_columns].corr()

print("Candidate variables:", len(candidate_columns))

print("\nCorrelation matrix:")
print(correlation_matrix.round(2).to_string())

# List strongly correlated pairs for review
print("\nVariable pairs with absolute correlation >= 0.70:")

found_pair = False

for i in range(len(candidate_columns)):
    for j in range(i + 1, len(candidate_columns)):
        first = candidate_columns[i]
        second = candidate_columns[j]
        correlation = correlation_matrix.loc[first, second]

        if pd.notna(correlation) and abs(correlation) >= 0.70:
            print(
                first,
                "<->",
                second,
                ":",
                round(correlation, 2)
            )
            found_pair = True

if not found_pair:
    print("No pairs met this threshold.")

# Save the matrix for later review
output_file = data_folder / "acs_candidate_correlations.csv"
correlation_matrix.to_csv(output_file)

print("\nCorrelation matrix saved to:")
print(output_file)
