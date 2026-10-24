
from pathlib import Path
import pandas as pd

from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parents[2]

raw_folder = project_folder / "data" / "raw" / "socioeconomic"
integrated_folder = project_folder / "data" / "processed" / "integrated"

files_to_check = [
    raw_folder / "acs_2019_kc_metro_candidate_data.csv",
    raw_folder / "acs_2019_kc_metro_cleaned.csv",
    integrated_folder / "kc_metro_combined_health_socioeconomic.csv"
]

keywords = [
    "population", "density", "disability",
    "employment", "employed", "labor",
    "unemployed", "poverty", "income"
]

for file_path in files_to_check:
    print("\n" + "=" * 60)
    print("FILE:", file_path.name)

    if not file_path.exists():
        print("File not found.")
        continue

    # Read only a few rows to inspect the column names
    df = pd.read_csv(file_path, nrows=5)

    print("Number of columns:", len(df.columns))
    print("\nRelevant column names:")

    found = False

    for column in df.columns:
        if any(word in column.lower() for word in keywords):
            print("-", column)
            found = True

    if not found:
        print("No matching columns found.")
