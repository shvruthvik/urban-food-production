
import pandas as pd
from pathlib import Path

# Set the data folder
project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "processed" / "integrated"

# Load the combined dataset
data = pd.read_csv(
    data_folder / "kc_metro_combined_health_socioeconomic.csv",
    dtype={"TractFIPS": str}
)

# Describe the candidate variables
variables = [
    {
        "Variable": "OBESITY_CrudePrev",
        "Category": "Community health",
        "Description": "Estimated adult obesity prevalence",
        "Source": "CDC PLACES, 2023 release",
        "Preliminary role": "Keep for initial review"
    },
    {
        "Variable": "DIABETES_CrudePrev",
        "Category": "Community health",
        "Description": "Estimated adult diabetes prevalence",
        "Source": "CDC PLACES, 2023 release",
        "Preliminary role": "Keep for initial review"
    },
    {
        "Variable": "BPHIGH_CrudePrev",
        "Category": "Community health",
        "Description": "Estimated adult high blood pressure prevalence",
        "Source": "CDC PLACES, 2023 release",
        "Preliminary role": "Keep for initial review"
    },
    {
        "Variable": "Poverty_Percent",
        "Category": "Socioeconomic need",
        "Description": "Percentage of people below the poverty level",
        "Source": "ACS 2019 5-year estimates",
        "Preliminary role": "Keep for initial review"
    },
    {
        "Variable": "No_Vehicle_Households_Percent",
        "Category": "Transportation access",
        "Description": "Percentage of households without a vehicle",
        "Source": "ACS 2019 5-year estimates",
        "Preliminary role": "Keep for initial review"
    },
    {
        "Variable": "SNAP_Households_Percent",
        "Category": "Economic and food assistance",
        "Description": "Percentage of households receiving SNAP",
        "Source": "ACS 2019 5-year estimates",
        "Preliminary role": "Compare with poverty"
    }
]

# Create a summary table
summary = pd.DataFrame(variables)

# Add data-quality information
summary["Valid tracts"] = summary["Variable"].apply(
    lambda column: data[column].notna().sum()
)

summary["Missing values"] = summary["Variable"].apply(
    lambda column: data[column].isna().sum()
)

summary["Mean"] = summary["Variable"].apply(
    lambda column: round(data[column].mean(), 2)
)

summary["Minimum"] = summary["Variable"].apply(
    lambda column: round(data[column].min(), 2)
)

summary["Maximum"] = summary["Variable"].apply(
    lambda column: round(data[column].max(), 2)
)

# Save the summary
output_file = data_folder / "kc_metro_variable_summary.csv"
summary.to_csv(output_file, index=False)

# Display the results
print(summary.to_string(index=False))
print("\nSummary saved to:", output_file)
