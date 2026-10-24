
import requests
import pandas as pd
from pathlib import Path
from getpass import getpass

# Project folders
project_folder = Path(__file__).resolve().parents[2]
integrated_folder = project_folder / "data" / "processed" / "integrated"
output_folder = project_folder / "data" / "raw" / "socioeconomic"

# Input: the 516 metro tracts from PLACES
places_file = integrated_folder / "kc_metro_tract_data.csv"

# Output: separate file for the 2019 ACS data
output_file = output_folder / "acs_2019_kc_metro_candidate_data.csv"

# Enter the API key privately
api_key = getpass("Enter your replacement Census API key: ")

# Read the PLACES tract IDs
places = pd.read_csv(places_file, dtype={"TractFIPS": str})
places["TractFIPS"] = places["TractFIPS"].str.zfill(11)
target_geoids = set(places["TractFIPS"])

print("PLACES tracts:", len(target_geoids))

# ACS variables already selected for candidate screening
variables = [
    "B01003_001E",
    "B19013_001E",
    "B17001_001E", "B17001_002E",
    "B05002_001E", "B05002_013E",
    "B08201_001E", "B08201_002E",
    "B22003_001E", "B22003_002E",
    "B03002_001E", "B03002_004E", "B03002_012E",
    "B11005_001E", "B11005_002E",
    "B15003_001E", "B15003_022E", "B15003_023E",
    "B15003_024E", "B15003_025E",
    "B25003_001E", "B25003_003E",
    "B25064_001E", "B25077_001E",
    "B01001_001E",
    "B01001_020E", "B01001_021E", "B01001_022E",
    "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E",
    "B18101_001E",
    "B18101_004E", "B18101_007E", "B18101_010E",
    "B18101_013E", "B18101_016E", "B18101_019E",
    "B18101_023E", "B18101_026E", "B18101_029E",
    "B18101_032E", "B18101_035E", "B18101_038E"
]

# Request data separately for each state, in manageable batches
all_state_data = []

for state in ["20", "29"]:
    print("\nDownloading 2019 ACS data for state:", state)

    state_batches = []

    for start in range(0, len(variables), 15):
        batch = variables[start:start + 15]

        params = {
            "get": ",".join(["NAME"] + batch),
            "for": "tract:*",
            "in": f"state:{state}",
            "key": api_key
        }

        response = requests.get(
            "https://api.census.gov/data/2019/acs/acs5",
            params=params,
            timeout=60
        )

        if response.status_code != 200:
            print("Request failed:", response.status_code)
            print(response.text)
            raise SystemExit("Download stopped. No final file was saved.")

        data = response.json()
        batch_df = pd.DataFrame(data[1:], columns=data[0])

        batch_df["GEOID"] = (
            batch_df["state"]
            + batch_df["county"]
            + batch_df["tract"]
        )

        batch_df = batch_df.drop(
            columns=["state", "county", "tract"]
        )

        state_batches.append(batch_df)

    # Combine the variable batches using the tract GEOID
    state_data = state_batches[0]

    for batch_df in state_batches[1:]:
        state_data = state_data.merge(
            batch_df,
            on=["NAME", "GEOID"],
            how="outer"
        )

    # Keep only tracts in the PLACES metro dataset
    state_data = state_data[
        state_data["GEOID"].isin(target_geoids)
    ].copy()

    all_state_data.append(state_data)

# Combine Kansas and Missouri
acs = pd.concat(all_state_data, ignore_index=True)

# Check matching and duplicates
print("\nPLACES unique tracts:", len(target_geoids))
print("ACS matched rows:", len(acs))
print("ACS unique GEOIDs:", acs["GEOID"].nunique())

matched_ids = set(acs["GEOID"])
unmatched_ids = sorted(target_geoids - matched_ids)

print("Unmatched PLACES tracts:", len(unmatched_ids))

if unmatched_ids:
    print("\nFirst 20 unmatched IDs:")
    print(unmatched_ids[:20])

# Convert candidate estimates to numeric
estimate_columns = [
    column for column in acs.columns
    if column.endswith("E")
]

for column in estimate_columns:
    acs[column] = pd.to_numeric(acs[column], errors="coerce")

# Calculate percentages safely
def safe_percent(numerator, denominator):
    numerator = pd.to_numeric(numerator, errors="coerce")
    denominator = pd.to_numeric(denominator, errors="coerce")
    denominator = denominator.where(denominator != 0)
    return numerator / denominator * 100

acs["Poverty_Percent"] = safe_percent(
    acs["B17001_002E"], acs["B17001_001E"]
)

acs["Foreign_Born_Percent"] = safe_percent(
    acs["B05002_013E"], acs["B05002_001E"]
)

acs["No_Vehicle_Households_Percent"] = safe_percent(
    acs["B08201_002E"], acs["B08201_001E"]
)

acs["SNAP_Households_Percent"] = safe_percent(
    acs["B22003_002E"], acs["B22003_001E"]
)

acs["Non_Hispanic_Black_Percent"] = safe_percent(
    acs["B03002_004E"], acs["B03002_001E"]
)

acs["Hispanic_Latino_Percent"] = safe_percent(
    acs["B03002_012E"], acs["B03002_001E"]
)

acs["Households_With_Children_Percent"] = safe_percent(
    acs["B11005_002E"], acs["B11005_001E"]
)

acs["Renter_Occupied_Percent"] = safe_percent(
    acs["B25003_003E"], acs["B25003_001E"]
)

# Fix education calculation by converting estimates to numbers first
education_columns = [
    "B15003_022E",
    "B15003_023E",
    "B15003_024E",
    "B15003_025E"
]

education_total = acs[education_columns].sum(axis=1, min_count=1)

acs["Bachelors_Or_Higher_Percent"] = safe_percent(
    education_total, acs["B15003_001E"]
)

# Calculate population aged 65 and older
age_columns = [
    "B01001_020E", "B01001_021E", "B01001_022E",
    "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E"
]

age_65_plus = acs[age_columns].sum(axis=1, min_count=1)

acs["Age_65_Plus_Percent"] = safe_percent(
    age_65_plus, acs["B01001_001E"]
)

# Save the results separately from the previous 2023 file
acs.to_csv(output_file, index=False)

print("\nSaved 2019 ACS candidate data to:")
print(output_file)

print("\nFinal rows:", len(acs))
print("Final unique GEOIDs:", acs["GEOID"].nunique())

print("\nPercentage calculation checks:")
percentage_columns = [
    "Poverty_Percent",
    "No_Vehicle_Households_Percent",
    "Bachelors_Or_Higher_Percent",
    "Age_65_Plus_Percent"
]

print(acs[percentage_columns].describe().round(2))

