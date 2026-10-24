
import pandas as pd
from pathlib import Path

data_folder = Path("data")
sram_file = data_folder / "2025-sram-fara-data.xlsx"

excel = pd.ExcelFile(sram_file)

sheets_to_check = [
    "VL_Driving Distance",
    "Driving Distance Data",
    "VL_Straight-Line Distance",
    "Straight-Line Distance Data"
]

for sheet_name in sheets_to_check:
    print("\n" + "=" * 70)
    print("WORKSHEET:", sheet_name)
    print("=" * 70)

    if sheet_name not in excel.sheet_names:
        print("Worksheet not found.")
        continue

    # Lookup sheets may have a different header layout.
    if sheet_name.startswith("VL_"):
        df = pd.read_excel(
            sram_file,
            sheet_name=sheet_name,
            header=None
        )
        print(df.head(20).to_string(index=False, header=False))
    else:
        df = pd.read_excel(
            sram_file,
            sheet_name=sheet_name,
            header=1,
            nrows=5
        )

        print("\nColumn names:")
        print(df.columns.tolist())

        print("\nSample records:")
        print(df.to_string(index=False))
