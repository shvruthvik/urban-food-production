
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
output_folder = project_folder / "data" / "processed" / "socioeconomic"
output_folder.mkdir(parents=True, exist_ok=True)

variables = [
    {
        "Variable": "Poverty percentage",
        "Dimension": "Socioeconomic need",
        "Decision": "Keep for initial model",
        "Reason": "Direct indicator of economic hardship",
        "Check": "Compare with SNAP and income"
    },
    {
        "Variable": "No-vehicle households percentage",
        "Dimension": "Transportation access",
        "Decision": "Keep for initial model",
        "Reason": "May indicate transportation barriers",
        "Check": "Compare with poverty and SNAP"
    },
    {
        "Variable": "SNAP households percentage",
        "Dimension": "Economic and food assistance",
        "Decision": "Compare with poverty",
        "Reason": "Indicates participation in food assistance",
        "Check": "Strong correlation with poverty"
    },
    {
        "Variable": "Median household income",
        "Dimension": "Socioeconomic context",
        "Decision": "Compare with poverty",
        "Reason": "Measures household economic conditions",
        "Check": "Strong correlation with poverty and home value"
    },
    {
        "Variable": "Obesity prevalence",
        "Dimension": "Community health",
        "Decision": "Keep for initial review",
        "Reason": "Health indicator identified in project context",
        "Check": "Verify source, year, and interpretation"
    },
    {
        "Variable": "Diabetes prevalence",
        "Dimension": "Community health",
        "Decision": "Keep for initial review",
        "Reason": "Health indicator identified in project context",
        "Check": "Verify source, year, and interpretation"
    },
    {
        "Variable": "High blood pressure prevalence",
        "Dimension": "Community health",
        "Decision": "Keep for initial review",
        "Reason": "Health indicator identified in project context",
        "Check": "Verify source, year, and interpretation"
    },
    {
        "Variable": "Age 65+ percentage",
        "Dimension": "Demographic context",
        "Decision": "Retain for review",
        "Reason": "May help describe community needs",
        "Check": "Justify its role in site prioritization"
    },
    {
        "Variable": "Bachelor's degree or higher percentage",
        "Dimension": "Education",
        "Decision": "Descriptive for now",
        "Reason": "May characterize neighborhood context",
        "Check": "Strong correlation with income and home value"
    },
    {
        "Variable": "Median rent",
        "Dimension": "Housing context",
        "Decision": "Descriptive for now",
        "Reason": "May characterize local housing conditions",
        "Check": "Correlated with income"
    },
    {
        "Variable": "Median home value",
        "Dimension": "Housing context",
        "Decision": "Descriptive for now",
        "Reason": "May characterize local housing conditions",
        "Check": "Strong correlation with income and education"
    },
    {
        "Variable": "Foreign-born percentage",
        "Dimension": "Demographic context",
        "Decision": "Descriptive for now",
        "Reason": "May support contextual analysis",
        "Check": "Do not interpret as a disadvantage by itself"
    },
    {
        "Variable": "Hispanic/Latino percentage",
        "Dimension": "Demographic context",
        "Decision": "Descriptive for now",
        "Reason": "May support contextual analysis",
        "Check": "Do not interpret as a disadvantage by itself"
    },
    {
        "Variable": "Households with children percentage",
        "Dimension": "Demographic context",
        "Decision": "Retain for review",
        "Reason": "May be relevant to family-oriented planning",
        "Check": "Define the intended planning rationale"
    }
]

df = pd.DataFrame(variables)

output_file = output_folder / "acs_variable_selection_summary.csv"
df.to_csv(output_file, index=False)

print("Candidate variables documented:", len(df))
print("\nVariable-selection summary:")
print(df.to_string(index=False))
print("\nSaved to:")
print(output_file)

