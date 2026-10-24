
import pandas as pd
from pathlib import Path

# Find the project folder
project_folder = Path(__file__).resolve().parents[2]

# Load the full health screening dataset
input_file = (
    project_folder
    / "data"
    / "processed"
    / "health"
    / "kc_metro_health_all_variables.csv"
)

output_file = (
    project_folder
    / "data"
    / "processed"
    / "health"
    / "health_variable_inventory.csv"
)

df = pd.read_csv(input_file, dtype={"TractFIPS": str})

# Select all health prevalence variables
health_columns = [
    col for col in df.columns
    if col.endswith("_CrudePrev")
]

# Calculate descriptive statistics
summary = df[health_columns].agg(
    ["count", "mean", "std", "min", "max"]
).T

summary["Missing"] = df[health_columns].isna().sum()
summary.index.name = "Variable"
summary = summary.reset_index()

# Save the inventory
summary.to_csv(output_file, index=False)

print("Health measures:", len(health_columns))
print("Rows in dataset:", len(df))
print("\nInventory preview:")
print(summary.round(2).to_string(index=False))
print("\nSaved:", output_file)
