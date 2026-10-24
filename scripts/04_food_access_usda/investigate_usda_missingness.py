from pathlib import Path
import pandas as pd

# 1. Set the file locations
DATA_FILE = Path("data/kc_metro_combined_health_socioeconomic_LRAM2019.csv")
REPORT_DIR = Path("data")

# 2. Define the columns we want to investigate
ID_COL = "TractFIPS"
SHARE_COL = "LRAM2019_lapop1share"
COUNT_COL = "LRAM2019_LAPOP1_10"

# 3. Check that the input file exists
if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"File not found: {DATA_FILE}. Run this script from your project folder."
    )

# 4. Load the merged project dataset
df = pd.read_csv(DATA_FILE, dtype={ID_COL: "string"})

# 5. Check whether the required columns exist
required_columns = [ID_COL, SHARE_COL, COUNT_COL]
missing_columns = [col for col in required_columns if col not in df.columns]

if missing_columns:
    raise KeyError(f"These columns are missing: {missing_columns}")

# 6. Convert the USDA indicators to numeric values
df[SHARE_COL] = pd.to_numeric(df[SHARE_COL], errors="coerce")
df[COUNT_COL] = pd.to_numeric(df[COUNT_COL], errors="coerce")

# 7. Identify missing values
df["Missing_lapop1share"] = df[SHARE_COL].isna()
df["Missing_LAPOP1_10"] = df[COUNT_COL].isna()

# 8. Classify each tract based on its missing values
def classify_missing_values(row):
    share_missing = row["Missing_lapop1share"]
    count_missing = row["Missing_LAPOP1_10"]

    if share_missing and count_missing:
        return "Both missing"
    elif share_missing:
        return "Share only missing"
    elif count_missing:
        return "Count only missing"
    else:
        return "Neither missing"


df["Missingness_pattern"] = df.apply(
    classify_missing_values, axis=1
)

# 9. Save a report containing every tract and its missingness status
context_columns = [
    "GEOID",
    "Geolocation",
    "POPULATION",
    "Population",
    "TotalPopulation",
    "B01003_001E",
    "Median_Household_Income",
    "MedianIncome",
    "B19013_001E",
    "Poverty",
    "Poverty_Rate",
    "No_Vehicle",
    "NoVehicle",
    "LRAM2019_LA1and10",
    "LRAM2019_LAhalfand10",
    "LRAM2019_LILATracts_1And10",
    "LRAM2019_LALOWI1_10",
    "LRAM2019_lalowi1share",
]

available_context_columns = [
    col for col in context_columns if col in df.columns
]

detail_columns = [
    ID_COL,
    SHARE_COL,
    COUNT_COL,
    "Missing_lapop1share",
    "Missing_LAPOP1_10",
    "Missingness_pattern",
] + [
    col for col in available_context_columns if col != ID_COL
]

df[detail_columns].to_csv(
    REPORT_DIR / "LRAM2019_missingness_by_tract.csv",
    index=False
)

# 10. Count the tracts in each missingness category
pattern_summary = (
    df.groupby("Missingness_pattern")
    .size()
    .reset_index(name="Tract_count")
)

pattern_summary["Percent_of_all_tracts"] = (
    pattern_summary["Tract_count"] / len(df) * 100
)

pattern_summary.to_csv(
    REPORT_DIR / "LRAM2019_missingness_pattern_summary.csv",
    index=False
)

# 11. Compare available numeric fields for missing vs. non-missing tracts
context_fields = [
    col for col in df.columns
    if any(
        word in col.lower()
        for word in [
            "population",
            "pop_",
            "income",
            "poverty",
            "vehicle",
            "la1and10",
            "lalowi",
        ]
    )
]

comparison_results = []

for column in context_fields:
    values = pd.to_numeric(df[column], errors="coerce")

    if values.notna().sum() == 0:
        continue

    groups = [
        ("Share missing", df["Missing_lapop1share"]),
        ("Share present", ~df["Missing_lapop1share"]),
        ("Count missing", df["Missing_LAPOP1_10"]),
        ("Count present", ~df["Missing_LAPOP1_10"]),
    ]

    for group_name, mask in groups:
        group_values = values[mask].dropna()

        comparison_results.append({
            "Indicator": (
                "lapop1share"
                if "Share" in group_name
                else "LAPOP1_10"
            ),
            "Group": group_name,
            "Context_column": column,
            "Tracts_in_group": int(mask.sum()),
            "Available_context_values": int(group_values.count()),
            "Mean": group_values.mean(),
            "Median": group_values.median(),
            "Minimum": group_values.min(),
            "Maximum": group_values.max(),
        })

comparison_df = pd.DataFrame(comparison_results)

comparison_df.to_csv(
    REPORT_DIR / "LRAM2019_missingness_context_comparison.csv",
    index=False
)

# 12. Print the results
print("=" * 60)
print("USDA MISSING-VALUE INVESTIGATION")
print("=" * 60)

print(f"Total rows: {len(df)}")
print(f"Unique tracts: {df[ID_COL].nunique()}")

print("\nMISSING VALUES")
print(f"{SHARE_COL}: {df[SHARE_COL].isna().sum()}")
print(f"{COUNT_COL}: {df[COUNT_COL].isna().sum()}")

print("\nMISSINGNESS PATTERNS")
print(pattern_summary.to_string(index=False))

print("\nAVAILABLE CONTEXT COLUMNS")
print(available_context_columns)

print("\nREPORTS CREATED")
print("1. data/LRAM2019_missingness_by_tract.csv")
print("2. data/LRAM2019_missingness_pattern_summary.csv")
print("3. data/LRAM2019_missingness_context_comparison.csv")

print("\nInvestigation completed.")
print("No missing values were filled, and the original dataset was not changed.")