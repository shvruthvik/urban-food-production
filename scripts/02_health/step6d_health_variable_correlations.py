
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
input_folder = project_folder / "data" / "processed" / "integrated"
output_folder = project_folder / "data" / "processed" / "health"

output_folder.mkdir(parents=True, exist_ok=True)

# Load the 516-tract health dataset
file_path = input_folder / "kc_metro_tract_data.csv"
df = pd.read_csv(file_path, dtype={"TractFIPS": str})

# Find the 36 candidate health variables
health_vars = [
    col for col in df.columns
    if col.endswith("_CrudePrev")
]

print("Health variables:", len(health_vars))
print("Census tracts:", df["TractFIPS"].nunique())

# Convert candidate values to numeric
for col in health_vars:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Calculate correlations between health variables
correlations = df[health_vars].corr(method="pearson")

# Save the complete correlation matrix
correlations.to_csv(
    output_folder / "health_variable_correlations.csv"
)

# Extract each unique pair only once
pairs = []

for i in range(len(health_vars)):
    for j in range(i + 1, len(health_vars)):
        pairs.append({
            "Variable_1": health_vars[i],
            "Variable_2": health_vars[j],
            "Correlation": correlations.iloc[i, j]
        })

pairs_df = pd.DataFrame(pairs)

# Sort by absolute correlation
pairs_df["Absolute_Correlation"] = (
    pairs_df["Correlation"].abs()
)

pairs_df = pairs_df.sort_values(
    "Absolute_Correlation",
    ascending=False
)

pairs_df.to_csv(
    output_folder / "health_variable_correlation_pairs.csv",
    index=False
)

print("\nTop 15 strongest correlation pairs:")
print(pairs_df.head(15).to_string(index=False))

print("\nSaved correlation results.")
