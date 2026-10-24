
from pathlib import Path
import pandas as pd

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "raw" / "socioeconomic"

for filename in [
    "acs_2019_kc_metro_candidate_data.csv",
    "acs_2019_kc_metro_cleaned.csv"
]:
    path = data_folder / filename

    print("\nFILE:", filename)

    if not path.exists():
        print("File not found.")
        continue

    df = pd.read_csv(path, nrows=2)

    for column in df.columns:
        print(column)
