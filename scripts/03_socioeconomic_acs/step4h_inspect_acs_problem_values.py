
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
raw_folder = project_folder / "data" / "raw" / "socioeconomic"
integrated_folder = project_folder / "data" / "processed" / "integrated"

acs_file = raw_folder / "acs_2019_kc_metro_candidate_data.csv"
places_file = integrated_folder / "kc_metro_tract_data.csv"

acs = pd.read_csv(acs_file, dtype={"GEOID": str})
places = pd.read_csv(places_file, dtype={"TractFIPS": str})

places["TractFIPS"] = places["TractFIPS"].str.zfill(11)

# Restore tract names and county information from PLACES
places_info = places[
    ["TractFIPS", "StateDesc", "CountyName"]
].drop_duplicates()

acs = acs.merge(
    places_info,
    left_on="GEOID",
    right_on="TractFIPS",
    how="left"
)

print("Rows after joining county information:", len(acs))
print("Missing county names:", acs["CountyName"].isna().sum())

# Inspect the tract with zero poverty denominator
print("\nTract with zero poverty denominator:")
poverty_columns = [
    "GEOID", "StateDesc", "CountyName",
    "B17001_001E", "B17001_002E",
    "B05002_001E", "B08201_001E",
    "B22003_001E", "B03002_001E",
    "B11005_001E", "B15003_001E",
    "B25003_001E", "B01001_001E", "B18101_001E"
]

print(
    acs.loc[
        acs["GEOID"] == "20209042501",
        poverty_columns
    ].to_string(index=False)
)

# Print all negative values in the three median estimates
for column in [
    "B19013_001E",
    "B25064_001E",
    "B25077_001E"
]:
    acs[column] = pd.to_numeric(acs[column], errors="coerce")

    problem_rows = acs[acs[column] < 0]

    print(f"\nNegative values in {column}:")
    print("Count:", len(problem_rows))

    print(
        problem_rows[
            ["GEOID", "StateDesc", "CountyName", column]
        ].to_string(index=False)
    )

# Save a separate diagnostic file with restored names
diagnostic_file = raw_folder / "acs_2019_candidate_diagnostic.csv"
acs.to_csv(diagnostic_file, index=False)

print("\nDiagnostic file saved to:")
print(diagnostic_file)
