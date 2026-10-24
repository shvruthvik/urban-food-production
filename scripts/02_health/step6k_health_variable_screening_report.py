
import pandas as pd
from pathlib import Path

# Folder containing the existing results
data_folder = Path("data")

# Load the results we already calculated
summary = pd.read_csv(
    data_folder / "health_sensitivity_summary.csv",
    index_col=0
)

correlations = pd.read_csv(
    data_folder / "health_sensitivity_correlations.csv",
    index_col=0
)

# Define the five variables we are reviewing
variables = [
    "OBESITY_CrudePrev",
    "DIABETES_CrudePrev",
    "BPHIGH_CrudePrev",
    "LPA_CrudePrev",
    "GHLTH_CrudePrev"
]

# Record the current screening decision for each variable
decisions = {
    "OBESITY_CrudePrev": (
        "Baseline",
        "Included in the professor's original health indicators."
    ),
    "DIABETES_CrudePrev": (
        "Baseline",
        "Included in the professor's original health indicators."
    ),
    "BPHIGH_CrudePrev": (
        "Baseline",
        "Included in the professor's original health indicators."
    ),
    "LPA_CrudePrev": (
        "Alternative",
        "Test as an alternative; strongly correlated with other indicators."
    ),
    "GHLTH_CrudePrev": (
        "Alternative",
        "Test as an alternative; strongly correlated with other indicators."
    )
}

# Create a table with the statistics and screening decisions
rows = []

for variable in variables:
    decision, reason = decisions[variable]

    rows.append({
        "Variable": variable,
        "Mean": summary.loc[variable, "Mean"],
        "Std_Dev": summary.loc[variable, "Std_Dev"],
        "Minimum": summary.loc[variable, "Minimum"],
        "Maximum": summary.loc[variable, "Maximum"],
        "Missing_Values": 0,
        "Screening_Status": decision,
        "Reason": reason
    })

screening_table = pd.DataFrame(rows)

# Save the screening table
screening_table.to_csv(
    data_folder / "health_variable_screening_table.csv",
    index=False
)

# Find the strongest correlations between different variables
pairs = []

for i in range(len(variables)):
    for j in range(i + 1, len(variables)):
        var1 = variables[i]
        var2 = variables[j]

        pairs.append({
            "Variable_1": var1,
            "Variable_2": var2,
            "Correlation": correlations.loc[var1, var2]
        })

correlation_pairs = pd.DataFrame(pairs)
correlation_pairs = correlation_pairs.sort_values(
    by="Correlation",
    ascending=False
)

correlation_pairs.to_csv(
    data_folder / "health_variable_correlation_pairs.csv",
    index=False
)

# Create a short written report
report_path = data_folder / "health_variable_screening_report.txt"

with open(report_path, "w", encoding="utf-8") as report:
    report.write("HEALTH VARIABLE SCREENING REPORT\n")
    report.write("Urban Food Production Project\n\n")

    report.write("Dataset: 516 Kansas City metro census tracts\n")
    report.write("Health variables reviewed: 5\n")
    report.write("Missing values: 0 for all five variables\n\n")

    report.write("BASELINE VARIABLES\n")
    report.write("- Obesity\n")
    report.write("- Diabetes\n")
    report.write("- High blood pressure\n\n")

    report.write("ALTERNATIVE VARIABLES\n")
    report.write("- Physical inactivity\n")
    report.write("- Fair or poor general health\n\n")

    report.write("STRONGEST CORRELATIONS\n")

    for _, pair in correlation_pairs.head(5).iterrows():
        report.write(
            f"- {pair['Variable_1']} and "
            f"{pair['Variable_2']}: "
            f"{pair['Correlation']:.3f}\n"
        )

    report.write("\nPRELIMINARY CONCLUSION\n")
    report.write(
        "The five health indicators show substantial overlap. "
        "The professor's three indicators are retained as the "
        "baseline for further evaluation. Physical inactivity "
        "and general health remain alternatives for testing. "
        "These results alone do not establish which variables "
        "are best for the final model. Final selection requires "
        "a clear rationale for how community health relates to "
        "urban food production priorities.\n"
    )

print("Health screening report created successfully.")
print("\nFiles created:")
print("1. data/health_variable_screening_table.csv")
print("2. data/health_variable_correlation_pairs.csv")
print("3. data/health_variable_screening_report.txt")
