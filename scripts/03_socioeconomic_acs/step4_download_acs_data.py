
import requests
import pandas as pd
from pathlib import Path
from getpass import getpass

# 1. Set up the project folders
project_folder = Path.cwd()
data_folder = project_folder / "data"

places_file = data_folder / (
    "PLACES__Census_Tract_Data_(GIS_Friendly_Format),_"
    "2023_release_20260112.csv"
)

# 2. Enter your Census API key privately
api_key = getpass("Enter your replacement Census API key: ")

# 3. Read the existing 516 PLACES census tracts
places_file = data_folder / "kc_metro_tract_data.csv"

places = pd.read_csv(
    places_file,
    dtype={"TractFIPS": str}
)

places["TractFIPS"] = places["TractFIPS"].str.zfill(11)

target_geoids = set(places["TractFIPS"].dropna())

print("PLACES metro tracts found:", len(target_geoids))

# 4. List the ACS variables we want to investigate
variables = [
    "B01003_001E",       # Total population
    "B19013_001E",       # Median household income
    "B17001_001E",       # Poverty-status population
    "B17001_002E",       # Population below poverty
    "B05002_001E",       # Total population for nativity table
    "B05002_013E",       # Foreign-born population
    "B08201_001E",       # Total households
    "B08201_002E",       # Households without a vehicle
    "B22003_001E",       # Total households for SNAP table
    "B22003_002E",       # Households receiving SNAP
    "B03002_001E",       # Total population for race/ethnicity table
    "B03002_004E",       # Non-Hispanic Black population
    "B03002_012E",       # Hispanic or Latino population
    "B11005_001E",       # Total households
    "B11005_002E",       # Households with children under 18
    "B15003_001E",       # Population age 25+ for education table
    "B15003_022E",       # Bachelor's degree
    "B15003_023E",       # Master's degree
    "B15003_024E",       # Professional degree
    "B15003_025E",       # Doctorate degree
    "B25003_001E",       # Total occupied housing units
    "B25003_003E",       # Renter-occupied housing units
    "B25064_001E",       # Median gross rent
    "B25077_001E",       # Median home value
    "B01001_001E",       # Total population for age table
    "B01001_020E", "B01001_021E", "B01001_022E",
    "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E",
    "B18101_001E",       # Total disability-table population
    "B18101_004E", "B18101_007E", "B18101_010E",
    "B18101_013E", "B18101_016E", "B18101_019E",
    "B18101_023E", "B18101_026E", "B18101_029E",
    "B18101_032E", "B18101_035E", "B18101_038E"
]

# 5. Download data for Missouri and Kansas in small batches
base_url = "https://api.census.gov/data/2023/acs/acs5"

all_data = []

# The API query is split into batches to keep requests manageable.
batch_size = 20

for state in ["20", "29"]:
    print("\nDownloading state:", state)

    state_data = None

    for start in range(0, len(variables), batch_size):
        batch = variables[start:start + batch_size]

        params = {
            "get": "NAME," + ",".join(batch),
            "for": "tract:*",
            "in": "state:" + state,
            "key": api_key
        }

        response = requests.get(
            base_url,
            params=params,
            timeout=60
        )

        if response.status_code != 200:
            print("Request failed:", response.status_code)
            print(response.text)
            raise SystemExit("Stopped because an API request failed.")

        data = response.json()
        batch_df = pd.DataFrame(
            data[1:],
            columns=data[0]
        )

        # Create a consistent 11-digit tract GEOID
        batch_df["GEOID"] = (
            batch_df["state"]
            + batch_df["county"]
            + batch_df["tract"]
        )

        batch_df = batch_df.drop(
            columns=["NAME", "state", "county", "tract"]
        )

        if state_data is None:
            state_data = batch_df
        else:
            state_data = state_data.merge(
                batch_df,
                on="GEOID",
                how="inner",
                validate="one_to_one"
            )

    all_data.append(state_data)

acs = pd.concat(all_data, ignore_index=True)

# 6. Keep only the tracts already in our PLACES dataset
acs = acs[acs["GEOID"].isin(target_geoids)].copy()

print("\nACS tracts matched:", len(acs))
print("Unique ACS GEOIDs:", acs["GEOID"].nunique())

if len(acs) != len(target_geoids):
    print("Warning: Some metro tract IDs did not match.")


# 7. Calculate candidate percentages
def safe_percent(numerator, denominator):
    denominator = pd.to_numeric(denominator, errors="coerce")
    numerator = pd.to_numeric(numerator, errors="coerce")

    return (numerator / denominator.replace(0, pd.NA)) * 100

acs["Poverty_Percent"] = safe_percent(
    acs["B17001_002E"], acs["B17001_001E"]
)

acs["Foreign_Born_Percent"] = safe_percent(
    acs["B05002_013E"], acs["B05002_001E"]
)

acs["No_Vehicle_Household_Percent"] = safe_percent(
    acs["B08201_002E"], acs["B08201_001E"]
)

acs["SNAP_Household_Percent"] = safe_percent(
    acs["B22003_002E"], acs["B22003_001E"]
)

acs["Black_NonHispanic_Percent"] = safe_percent(
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

education_total = (
    acs["B15003_022E"]
    + acs["B15003_023E"]
    + acs["B15003_024E"]
    + acs["B15003_025E"]
)

acs["Bachelors_Or_Higher_Percent"] = safe_percent(
    education_total, acs["B15003_001E"]
)

age_65_columns = [
    "B01001_020E", "B01001_021E", "B01001_022E",
    "B01001_023E", "B01001_024E", "B01001_025E",
    "B01001_044E", "B01001_045E", "B01001_046E",
    "B01001_047E", "B01001_048E", "B01001_049E"
]

# Convert the age estimates from text to numbers
for column in age_65_columns:
    acs[column] = pd.to_numeric(acs[column], errors="coerce")

# Add the age-group estimates
acs["Age_65_Plus_Count"] = acs[age_65_columns].sum(axis=1)

acs["Age_65_Plus_Percent"] = safe_percent(
    acs["Age_65_Plus_Count"], acs["B01001_001E"]
)

# 8. Save the ACS candidate dataset
output_file = data_folder / "acs_kc_metro_candidate_data.csv"

acs.to_csv(output_file, index=False)

print("\nSaved ACS data to:")
print(output_file)

print("\nFinal row count:", len(acs))
print("Final unique GEOIDs:", acs["GEOID"].nunique())

print("\nFirst five rows:")
print(acs.head().to_string(index=False))
