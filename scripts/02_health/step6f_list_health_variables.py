
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
input_file = (
    project_folder
    / "data"
    / "processed"
    / "health"
    / "kc_metro_health_all_variables.csv"
)

# Load one row to read the column names
df = pd.read_csv(
    input_file,
    nrows=1
)

# Print all health prevalence variables
print("Health variables in the dataset:\n")

for col in df.columns:
    if col.endswith("_CrudePrev"):
        print(col)
