from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "processed" / "integrated"

kc_file = data_folder / "kc_metro_tract_data.csv"

print("File exists:", kc_file.exists())

if kc_file.exists():
    kc = pd.read_csv(kc_file)

    print("Number of rows:", len(kc))
    print("Number of unique census tracts:", kc["TractFIPS"].nunique())
    print("Column names:")
    print(kc.columns.tolist())