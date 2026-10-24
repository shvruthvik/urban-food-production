
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
input_folder = project_folder / "data" / "processed" / "health"
output_folder = project_folder / "data" / "processed" / "health"

output_folder.mkdir(parents=True, exist_ok=True)

# Load the Kansas City metro health dataset
file_path = input_folder / "kc_metro_health_all_variables.csv"
df = pd.read_csv(file_path, dtype={"TractFIPS": str})

# Select all 36 health prevalence columns
health_columns = [
    col for col in df.columns
    if col.endswith("_CrudePrev")
]

health_data = df[health_columns].apply(
    pd.to_numeric, errors="coerce"
)

print("Number of census tracts:", len(df))
print("Number of health variables:", len(health_columns))

# Check whether any columns are exact duplicates
print("\nChecking for duplicate health columns...")

duplicate_pairs = []

for i in range(len(health_columns)):
    for j in range(i + 1, len(health_columns)):
        col1 = health_columns[i]
        col2 = health_columns[j]

        if health_data[col1].equals(health_data[col2]):
            duplicate_pairs.append((col1, col2))

if duplicate_pairs:
    print("Exact duplicate columns found:")
    for pair in duplicate_pairs:
        print(pair)
else:
    print("No exact duplicate columns found.")

# Recalculate the correlations
correlations = health_data.corr()

print("\nChecking the strongest correlations...")

for col1, col2 in [
    ("VISION_CrudePrev", "SELFCARE_CrudePrev"),
    ("GHLTH_CrudePrev", "INDEPLIVE_CrudePrev"),
    ("KIDNEY_CrudePrev", "STROKE_CrudePrev"),
    ("BPHIGH_CrudePrev", "KIDNEY_CrudePrev"),
    ("DIABETES_CrudePrev", "STROKE_CrudePrev")
]:
    if col1 in correlations.columns and col2 in correlations.columns:
        print(
            col1, "vs", col2, ":",
            round(correlations.loc[col1, col2], 4)
        )

# Save the recalculated correlation matrix
correlations.to_csv(
    output_folder / "health_variable_correlations_verified.csv"
)

print("\nVerification finished.")
