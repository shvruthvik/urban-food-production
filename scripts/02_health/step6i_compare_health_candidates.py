
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
input_folder = project_folder / "data" / "processed" / "health"
output_folder = project_folder / "data" / "processed" / "health"

output_folder.mkdir(parents=True, exist_ok=True)

# Load the professor-provided health dataset
input_file = input_folder / "kc_metro_health_all_variables.csv"
df = pd.read_csv(input_file)

# Select six health variables for comparison
variables = [
    "OBESITY_CrudePrev",
    "DIABETES_CrudePrev",
    "BPHIGH_CrudePrev",
    "LPA_CrudePrev",
    "GHLTH_CrudePrev",
    "DEPRESSION_CrudePrev"
]

# Calculate basic statistics
results = []

for variable in variables:
    results.append({
        "Variable": variable,
        "Mean_percent": df[variable].mean(),
        "Standard_deviation": df[variable].std(),
        "Minimum_percent": df[variable].min(),
        "Maximum_percent": df[variable].max(),
        "Missing_values": df[variable].isna().sum()
    })

summary = pd.DataFrame(results)

# Calculate correlations between the six variables
correlations = df[variables].corr()

# Save both outputs
summary.to_csv(
    output_folder / "health_candidate_comparison.csv",
    index=False
)

correlations.to_csv(
    output_folder / "health_candidate_correlations.csv"
)

print("HEALTH CANDIDATE SUMMARY")
print(summary.round(2).to_string(index=False))

print("\nCORRELATIONS BETWEEN CANDIDATES")
print(correlations.round(3).to_string())

print("\nFiles saved:")
print(output_folder / "health_candidate_comparison.csv")
print(output_folder / "health_candidate_correlations.csv")
