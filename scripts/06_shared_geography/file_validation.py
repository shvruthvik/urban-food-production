from pathlib import Path
import pandas as pd

data_folder = Path(
    r"C:\Users\shvru\Downloads\Urban food Production\data"
)

kc_file = data_folder / "kc_metro_tract_data.csv"

print("File exists:", kc_file.exists())

if kc_file.exists():
    kc = pd.read_csv(kc_file)

    print("Number of rows:", len(kc))
    print("Number of unique census tracts:", kc["TractFIPS"].nunique())
    print("Column names:")
    print(kc.columns.tolist())