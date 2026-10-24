
import pandas as pd

file_path = "data/2025-sram-fara-data.xlsx"

excel = pd.ExcelFile(file_path)

for sheet in excel.sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet, header=None)
    matches = df.astype(str).apply(
        lambda column: column.str.contains(
            "DD_SRAM_lahunvhalfshare",
            case=False,
            na=False
        )
    ).any(axis=1)

    if matches.any():
        print("\nSHEET:", sheet)
        print(df.loc[matches].to_string(index=False, header=False))
