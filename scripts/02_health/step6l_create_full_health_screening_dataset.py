
import pandas as pd
from pathlib import Path

# Find the project folder
project_folder = Path(__file__).resolve().parents[2]

# Set the input and output paths
input_file = (
    project_folder
    / "data"
    / "raw"
    / "health"
    / "PLACES__Census_Tract_Data_(GIS_Friendly_Format),_2023_release_20260112.csv"
)

output_folder = project_folder / "data" / "processed" / "health"
output_folder.mkdir(parents=True, exist_ok=True)

output_file = output_folder / "kc_metro_health_all_variables.csv"

# Define the 14 Kansas City metro counties
kc_metro_counties = {
    "29013", "29025", "29037", "29047",
    "29049", "29095", "29107", "29165",
    "29177", "20091", "20103", "20107",
    "20121", "20209"
}

# Load the original PLACES data
df = pd.read_csv(input_file, dtype={"CountyFIPS": str})
df["CountyFIPS"] = df["CountyFIPS"].str.zfill(5)

# Filter to the Kansas City metro counties
kc = df[df["CountyFIPS"].isin(kc_metro_counties)].copy()

# Find all crude prevalence measures
health_vars = [
    col for col in kc.columns
    if col.endswith("_CrudePrev")
]

# Keep geography information and all health measures
geo_cols = [
    "StateAbbr",
    "StateDesc",
    "CountyName",
    "CountyFIPS",
    "TractFIPS",
    "TotalPopulation",
    "Geolocation"
]

keep_cols = [col for col in geo_cols if col in kc.columns]
keep_cols += health_vars

health_data = kc[keep_cols].copy()

# Save the separate screening dataset
health_data.to_csv(output_file, index=False)

# Display basic checks
print("Total rows:", len(health_data))
print("Unique census tracts:", health_data["TractFIPS"].nunique())
print("Health measures:", len(health_vars))
print("Output saved to:", output_file)

