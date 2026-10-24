
from pathlib import Path
import pandas as pd

folder = Path("data/tract_boundaries")

files = [
    folder / "tab20_tract20_tract10_st20.txt",
    folder / "tab20_tract20_tract10_st29.txt"
]

for file in files:
    print("\n" + "=" * 60)
    print("FILE:", file.name)
    print("=" * 60)

    if not file.exists():
        print("File not found:", file)
        continue

    # These files are pipe-delimited and contain a header row
    df = pd.read_csv(file, sep="|", dtype=str, nrows=5)

    print("Number of columns:", len(df.columns))
    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nFirst five rows:")
    print(df.to_string(index=False))
