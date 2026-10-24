
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# STEP 1: Set the USDA workbook path
# --------------------------------------------------

file_path = Path("data/2025-sram-fara-data.xlsx")

if not file_path.exists():
    raise FileNotFoundError(f"File not found: {file_path}")

# --------------------------------------------------
# STEP 2: List the available worksheets
# --------------------------------------------------

excel = pd.ExcelFile(file_path)

print("USDA FOOD-ACCESS FIELD INSPECTION")
print("=" * 55)

print("\nAvailable worksheets:")
for sheet in excel.sheet_names:
    print("-", sheet)

# --------------------------------------------------
# STEP 3: Inspect the tract-level worksheet
# --------------------------------------------------

sheet_name = "GeneralTractCharacteristic Data"

sram = pd.read_excel(
    file_path,
    sheet_name=sheet_name,
    header=1
)

print("\nWORKSHEET:", sheet_name)
print("Number of rows:", len(sram))
print("Number of columns:", len(sram.columns))

# --------------------------------------------------
# STEP 4: Find population and food-access fields
# --------------------------------------------------

keywords = [
    "censustract20",
    "pop2020",
    "ohu2020",
    "dd_sram",
    "lapop",
    "lila",
    "lowaccess",
    "low_access",
    "lowincome",
    "tractlowi",
    "tracthunv",
    "share"
]

relevant_columns = [
    column for column in sram.columns
    if any(
        keyword in str(column).lower()
        for keyword in keywords
    )
]

print("\nRELEVANT FIELDS")
print("-" * 55)

for column in relevant_columns:
    print(column)

# --------------------------------------------------
# STEP 5: Check tract IDs
# --------------------------------------------------

if "CensusTract20" in sram.columns:
    tract_ids = sram["CensusTract20"].astype("string").str.strip()

    print("\nTRACT ID CHECK")
    print("-" * 55)
    print("Nonmissing tract IDs:", tract_ids.notna().sum())
    print("Unique nonmissing tract IDs:", tract_ids.nunique())
    print("Missing tract IDs:", tract_ids.isna().sum())

# --------------------------------------------------
# STEP 6: Display sample population and access fields
# --------------------------------------------------

sample_columns = [
    "CensusTract20",
    "POP2020",
    "OHU2020",
    "LowIncomeTracts",
    "TractLOWI",
    "TractHUNV",
    "DD_SRAM_LA1and10",
    "DD_SRAM_LILATracts_1And10",
    "DD_SRAM_lapop1",
    "DD_SRAM_lapop1share",
    "DD_SRAM_LAPOP1_10"
]

available_sample_columns = [
    column for column in sample_columns
    if column in sram.columns
]

print("\nSAMPLE VALUES FROM AVAILABLE FIELDS")
print("-" * 55)

if available_sample_columns:
    print(
        sram[available_sample_columns]
        .head(10)
        .to_string(index=False)
    )
else:
    print("None of the requested sample fields were found.")

# --------------------------------------------------
# STEP 7: Inspect the driving-distance worksheet
# --------------------------------------------------

driving_sheet = "Driving Distance Data"

if driving_sheet in excel.sheet_names:
    driving = pd.read_excel(
        file_path,
        sheet_name=driving_sheet,
        header=1
    )

    print("\nWORKSHEET:", driving_sheet)
    print("Number of rows:", len(driving))
    print("Number of columns:", len(driving.columns))

    driving_columns = [
        column for column in driving.columns
        if any(
            keyword in str(column).lower()
            for keyword in [
                "censustract20",
                "dd_sram",
                "lapop",
                "lila",
                "lowaccess",
                "low_access",
                "pop"
            ]
        )
    ]

    print("\nRELEVANT DRIVING-DISTANCE FIELDS")
    print("-" * 55)

    for column in driving_columns:
        print(column)

    driving_sample_columns = [
        column for column in sample_columns
        if column in driving.columns
    ]

    if driving_sample_columns:
        print("\nSAMPLE VALUES FROM DRIVING-DISTANCE DATA")
        print("-" * 55)
        print(
            driving[driving_sample_columns]
            .head(10)
            .to_string(index=False)
        )
else:
    print(f"\nWorksheet not found: {driving_sheet}")

print("\nInspection complete. No source data was modified.")
