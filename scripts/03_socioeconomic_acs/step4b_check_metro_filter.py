
import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
raw_folder = project_folder / "data" / "raw" / "health"
output_folder = project_folder / "data" / "processed" / "integrated"

places_file = raw_folder / (
    "PLACES__Census_Tract_Data_(GIS_Friendly_Format),_"
    "2023_release_20260112.csv"
)

places = pd.read_csv(places_file, dtype={"TractFIPS": str})

# Convert tract IDs to consistent 11-digit strings
places["TractFIPS"] = places["TractFIPS"].str.zfill(11)

# Kansas City metro counties: 9 in Missouri and 5 in Kansas

metro_counties = {
    # Missouri counties
    "29013",  # Bates
    "29025",  # Caldwell
    "29037",  # Cass
    "29047",  # Clay
    "29049",  # Clinton
    "29095",  # Jackson
    "29107",  # Lafayette
    "29165",  # Platte
    "29177",  # Ray

    # Kansas counties
    "20091",  # Johnson
    "20103",  # Leavenworth
    "20107",  # Linn
    "20121",  # Miami
    "20209",  # Wyandotte
}


# Build a 5-digit state + county FIPS code
places["CountyKey"] = (
    places["TractFIPS"].str[:2]
    + places["TractFIPS"].str[2:5]
)

metro = places[places["CountyKey"].isin(metro_counties)].copy()

print("Nationwide PLACES rows:", len(places))
print("Metro rows:", len(metro))
print("Unique metro tract IDs:", metro["TractFIPS"].nunique())
print("\nTracts by county:")
print(metro.groupby(["StateDesc", "CountyName"]).size().to_string())

# Save the filtered PLACES dataset for later use
output_file = output_folder / "kc_metro_tract_data.csv"
metro.drop(columns=["CountyKey"]).to_csv(output_file, index=False)

print("\nSaved filtered PLACES data to:")
print(output_file)

