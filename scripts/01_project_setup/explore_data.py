import pandas as pd
from pathlib import Path

# pd.set_option("display.max_columns", None)

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data"

data_files = list(data_folder.rglob("*.csv"))

for file in data_files:
    print(file.name)


for file in data_files:

    print("\n" + "=" * 60)
    print("FILE:", file.name)
    print("=" * 60)

    df = pd.read_csv(file, nrows=10)

    print("\nNumber of columns:", len(df.columns))
    print("\nColumn names:", df.columns.tolist())
    print("\nFirst 5 rows:", df.head().to_string(index=False))
    print("\nData types:", df.dtypes.to_string())

    row_count = 0

    for chunk in pd.read_csv(file, chunksize=100000):
        row_count = row_count + len(chunk)

    print("\nTotal number of rows:", row_count)

    missing_values = {}

    for chunk in pd.read_csv(file, chunksize=100000):

        for column in chunk.columns:

            if column not in missing_values:
                missing_values[column] = 0

            missing_values[column] = (
                missing_values[column] +
                chunk[column].isnull().sum()
            )

    print("\nMissing values for", file.name, ":")

    for column, count in missing_values.items():

        if count > 0:
            print(column, ":", count)