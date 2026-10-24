
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

# Save the health variable selection table
output_file = (
    project_folder
    / "data"
    / "processed"
    / "health"
    / "health_variable_selection_table.csv"
)

# Read the data
df = pd.read_csv(input_file, dtype={"TractFIPS": str})

# Group health variables by category
groups = {
    "Chronic health outcomes": [
        "ARTHRITIS", "BPHIGH", "CANCER", "CASTHMA",
        "CHD", "COPD", "DIABETES", "HIGHCHOL",
        "KIDNEY", "OBESITY", "STROKE"
    ],
    "Health behaviors": [
        "BINGE", "CSMOKING", "LPA", "SLEEP"
    ],
    "General health": [
        "DEPRESSION", "GHLTH", "MHLTH", "PHLTH"
    ],
    "Prevention and healthcare": [
        "ACCESS2", "BPMED", "CERVICAL", "CHECKUP",
        "CHOLSCREEN", "COLON_SCREEN", "COREM",
        "COREW", "DENTAL", "MAMMOUSE"
    ],
    "Disability and functioning": [
        "DISABILITY", "HEARING", "VISION", "COGNITION",
        "SELFCARE", "INDEPLIVE"
    ],
    "Other health measures": [
        "TEETHLOST"
    ]
}

# Create one row for each health measure
rows = []

for col in df.columns:
    if not col.endswith("_CrudePrev"):
        continue

    name = col.replace("_CrudePrev", "")
    group = "Review classification"

    for category, variables in groups.items():
        if name in variables:
            group = category
            break

    rows.append({
        "Variable": name,
        "Group": group,
        "Missing_values": df[col].isna().sum(),
        "Mean": df[col].mean(),
        "Standard_deviation": df[col].std(),
        "Minimum": df[col].min(),
        "Maximum": df[col].max(),
        "Decision": "Review",
        "Reason": "Assess project relevance and overlap"
    })

# Convert the results into a table
result = pd.DataFrame(rows)

# Create the output folder if needed
output_file.parent.mkdir(parents=True, exist_ok=True)

# Save the table
result.to_csv(output_file, index=False)

# Display the results
print("Health measures reviewed:", len(result))
print("Rows in source dataset:", len(df))
print("Variables with missing values:", (result["Missing_values"] > 0).sum())
print("\nSelection table preview:")
print(result.round(2).to_string(index=False))

print("\nSaved:", output_file)
