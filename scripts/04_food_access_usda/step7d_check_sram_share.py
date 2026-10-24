
import pandas as pd

file_path = "data/2025-sram-fara-data.xlsx"

df = pd.read_excel(
    file_path,
    sheet_name="Driving Distance Data",
    header=1
)

tract_id = "29095989100"

ids = (
    df["CensusTract20"]
    .astype(str)
    .str.replace(r"\.0$", "", regex=True)
    .str.strip()
    .str.zfill(11)
)

row = df.loc[ids == tract_id]

if row.empty:
    print("Tract not found.")
else:
    record = row.iloc[0].dropna()
    print(record.to_string())
