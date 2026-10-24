
import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
data_folder = folder / "data"

source_file = data_folder / "2025-sram-fara-data.xlsx"
study_file = data_folder / "sram_kc_metro_2020_tracts.csv"

# Read the USDA driving-distance worksheet using its real header row
driving = pd.read_excel(
    source_file,
    sheet_name="Driving Distance Data",
    header=1,
    dtype={"CensusTract20": str}
)

# Read the 607 study-area tract IDs
study = pd.read_csv(
    study_file,
    dtype={"CensusTract20": str}
)

# Select only the study-area tracts
columns = [
    "CensusTract20",
    "DD_SRAM_LA1and10",
    "DD_SRAM_LILATracts_1And10",
    "DD_SRAM_lapop1share",
    "DD_SRAM_lapop1",
    "DD_SRAM_LAPOP1_10"
]

study_ids = set(study["CensusTract20"].str.strip())
driving["CensusTract20"] = driving["CensusTract20"].str.strip()

filtered = driving[
    driving["CensusTract20"].isin(study_ids)
][columns].copy()

print("Study-area IDs:", len(study_ids))
print("USDA records found:", len(filtered))
print("Duplicate tract IDs:", filtered["CensusTract20"].duplicated().sum())

print("\nIndicator summary:")

for column in columns[1:]:
    values = pd.to_numeric(filtered[column], errors="coerce")

    print(f"\n{column}")
    print("Non-missing:", values.notna().sum())
    print("Missing:", values.isna().sum())
    print("Minimum:", values.min())
    print("Maximum:", values.max())

    if column in [
        "DD_SRAM_LA1and10",
        "DD_SRAM_LILATracts_1And10"
    ]:
        print("Value counts:")
        print(values.value_counts(dropna=False).to_string())

print("\nInspection complete. No files were modified.")
