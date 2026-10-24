
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "raw" / "health"

places_file = data_folder / (
    "PLACES__Census_Tract_Data_(GIS_Friendly_Format),_"
    "2023_release_20260112.csv"
)

places = pd.read_csv(places_file)

print("Number of rows:", len(places))
print("\nRelevant columns:")
print([
    col for col in places.columns
    if "tract" in col.lower()
    or "county" in col.lower()
    or "state" in col.lower()
])

print("\nFirst five tract IDs:")
print(places["TractFIPS"].head().to_list())

print("\nTractFIPS data type:")
print(places["TractFIPS"].dtype)

print("\nFirst five county names:")
print(places["CountyName"].head().to_list())
