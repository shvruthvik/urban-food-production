
import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
file_path = folder / "data" / "2025-sram-fara-data.xlsx"

# The actual column headers are on the second row
df = pd.read_excel(
    file_path,
    sheet_name="Driving Distance Data",
    header=1
)

print("DATASET SHAPE:", df.shape)

columns = [
    "CensusTract20",
    "DD_SRAM_LA1and10",
    "DD_SRAM_LILATracts_1And10",
    "DD_SRAM_lapop1share",
    "DD_SRAM_lapop1",
    "DD_SRAM_LAPOP1_10"
]

for column in columns:
    if column not in df.columns:
        print(f"\n{column}: NOT FOUND")
        continue

    values = df[column]
    print(f"\n--- {column} ---")
    print("Non-missing:", values.notna().sum())
    print("Missing:", values.isna().sum())
    print("Unique values:", values.nunique())
    print("Most common values:")
    print(values.value_counts(dropna=False).head(6).to_string())

    if column != "CensusTract20":
        numeric = pd.to_numeric(values, errors="coerce")
        print("Minimum:", numeric.min())
        print("Maximum:", numeric.max())

print("\nInspection complete.")
