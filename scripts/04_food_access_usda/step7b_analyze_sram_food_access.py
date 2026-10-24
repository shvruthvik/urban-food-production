
import pandas as pd
from pathlib import Path

data_folder = Path("data")
sram_file = data_folder / "2025-sram-fara-data.xlsx"

output_summary = data_folder / "sram_food_access_summary.csv"
output_counties = data_folder / "sram_food_access_by_county.csv"
output_report = data_folder / "sram_food_access_screening.txt"

# Read the driving-distance data
sram = pd.read_excel(
    sram_file,
    sheet_name="Driving Distance Data",
    header=1
)

# Normalize state and county names
sram["State_clean"] = sram["State"].astype("string").str.strip().str.casefold()
sram["County_clean"] = (
    sram["County20"]
    .astype("string")
    .str.strip()
    .str.casefold()
)

if "County24" in sram.columns:
    sram["County24_clean"] = (
        sram["County24"]
        .astype("string")
        .str.strip()
        .str.casefold()
    )

# Define the project counties
study_counties = {
    ("kansas", "johnson county"),
    ("kansas", "leavenworth county"),
    ("kansas", "linn county"),
    ("kansas", "miami county"),
    ("kansas", "wyandotte county"),
    ("missouri", "bates county"),
    ("missouri", "caldwell county"),
    ("missouri", "cass county"),
    ("missouri", "clay county"),
    ("missouri", "clinton county"),
    ("missouri", "jackson county"),
    ("missouri", "lafayette county"),
    ("missouri", "platte county"),
    ("missouri", "ray county"),
}

sram["In_Study_Area"] = [
    (state, county) in study_counties
    for state, county in zip(
        sram["State_clean"],
        sram["County_clean"]
    )
]

kc = sram[sram["In_Study_Area"]].copy()

# Candidate indicators to examine
candidate_columns = [
    "DD_SRAM_LA1and10",
    "DD_SRAM_LILATracts_1And10",
    "DD_SRAM_lapop1share",
    "DD_SRAM_lapophalfshare",
    "DD_SRAM_lahunvhalfshare",
]

# Confirm that the requested fields exist
missing_columns = [
    column for column in candidate_columns
    if column not in kc.columns
]

if missing_columns:
    raise ValueError(
        f"These columns were not found: {missing_columns}"
    )

# Convert candidate fields to numeric
for column in candidate_columns:
    kc[column] = pd.to_numeric(
        kc[column],
        errors="coerce"
    )

# Overall summary
summary_rows = []

for column in candidate_columns:
    values = kc[column].dropna()

    row = {
        "Variable": column,
        "Tracts_With_Value": len(values),
        "Missing_Values": int(kc[column].isna().sum()),
        "Minimum": values.min() if len(values) else None,
        "Maximum": values.max() if len(values) else None,
        "Mean": values.mean() if len(values) else None,
        "Median": values.median() if len(values) else None,
    }

    # For binary flag fields, count the 1s and 0s
    if column in [
        "DD_SRAM_LA1and10",
        "DD_SRAM_LILATracts_1And10",
    ]:
        row["Tracts_Flagged_1"] = int((values == 1).sum())
        row["Tracts_Flagged_0"] = int((values == 0).sum())

    summary_rows.append(row)

summary = pd.DataFrame(summary_rows)
summary.to_csv(output_summary, index=False)

# County-level summary
county_rows = []

for (state, county), group in kc.groupby(
    ["State", "County20"],
    dropna=False
):
    row = {
        "State": state,
        "County": county,
        "Tracts": len(group),
    }

    for column in [
        "DD_SRAM_LA1and10",
        "DD_SRAM_LILATracts_1And10",
    ]:
        values = group[column].dropna()
        row[column + "_flagged_count"] = int((values == 1).sum())
        row[column + "_valid_count"] = len(values)

    county_rows.append(row)

county_summary = pd.DataFrame(county_rows)
county_summary.to_csv(output_counties, index=False)

# Text report
report = f"""
SRAM FOOD-ACCESS SCREENING
==========================

SRAM rows in study counties: {len(kc)}
Unique tract IDs: {kc['CensusTract20'].nunique()}

Candidate indicator summary:
{summary.to_string(index=False)}

Important limitations:
1. SRAM uses 2020 tract geography.
2. Existing project boundaries use 2019 tract geography.
3. These results are descriptive screening results, not suitability scores.
4. SNAP-authorized retailers are not necessarily all supermarkets
   or full-service grocery stores.
5. Population shares and tract flags measure different things.
6. Food access is not the same as public transit access.
7. Review the official lookup definitions before final variable selection.
"""

output_report.write_text(report, encoding="utf-8")

print(report)
print("\nSaved files:")
print(output_summary)
print(output_counties)
print(output_report)
