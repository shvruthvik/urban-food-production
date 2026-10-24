
import pandas as pd
from pathlib import Path

# Set the project and data folders
project_folder = Path(__file__).resolve().parents[2]

input_folder = project_folder / "data" / "processed" / "health"

file_path = input_folder / "kc_metro_health_all_variables.csv"

# Load the existing combined dataset
data = pd.read_csv(file_path, dtype={"TractFIPS": str})

# Select the three original and two alternative health variables
health_vars = [
    "OBESITY_CrudePrev",
    "DIABETES_CrudePrev",
    "BPHIGH_CrudePrev",
    "LPA_CrudePrev",
    "GHLTH_CrudePrev"
]

# Check whether all five variables exist
missing_columns = [col for col in health_vars if col not in data.columns]

if missing_columns:
    print("These columns are missing from the combined dataset:")
    print(missing_columns)
    print("\nAvailable columns containing health measures:")
    print([col for col in data.columns if "CrudePrev" in col])
else:
    # Keep only the five health variables
    health_data = data[health_vars].copy()

    # Display basic information
    print("Number of census tracts:", len(data))
    print("\nMissing values:")
    print(health_data.isna().sum())

    # Calculate summary statistics
    summary = health_data.describe().T
    summary = summary[["mean", "std", "min", "max"]].round(3)
    summary.columns = ["Mean", "Std_Dev", "Minimum", "Maximum"]

    # Calculate correlations between health variables
    correlations = health_data.corr().round(3)

    # Save the results
    output_folder = project_folder / "data" / "processed" / "health"
    output_folder.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_folder / "health_sensitivity_summary.csv")
    correlations.to_csv(output_folder / "health_sensitivity_correlations.csv")

    print("\nHealth variable summary:")
    print(summary)

    print("\nHealth variable correlations:")
    print(correlations)

    print("\nFiles saved:")
    print(output_folder / "health_sensitivity_summary.csv")
    print(output_folder / "health_sensitivity_correlations.csv")
