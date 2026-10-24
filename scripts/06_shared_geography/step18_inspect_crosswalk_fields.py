
import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
file_path = (
    folder / "data" /
    "kc_metro_2010_2020_tract_relationships_complete.csv"
)

df = pd.read_csv(file_path, dtype=str)

print("CROSSWALK SHAPE:", df.shape)

print("\nALL COLUMNS:")
for column in df.columns:
    print(column)

print("\nFIRST 10 ROWS:")
print(df.head(10).to_string(index=False))

print("\nMISSING VALUES:")
print(df.isna().sum().to_string())

print("\nInspection complete. No files were modified.")
