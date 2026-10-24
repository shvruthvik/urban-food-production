
import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
file_path = folder / "data" / "sram_kc_metro_2020_tracts.csv"

df = pd.read_csv(file_path, dtype=str)

print("DATASET SHAPE:", df.shape)
print("\nALL COLUMN NAMES:")

for column in df.columns:
    print(column)

print("\nCOLUMNS RELATED TO FOOD ACCESS:")

for column in df.columns:
    if any(word in column.lower() for word in [
        "access", "sram", "lapop", "lowi",
        "hunv", "snap", "tract"
    ]):
        print(column)

print("\nInspection complete.")
