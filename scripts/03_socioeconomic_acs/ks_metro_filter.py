import pandas as pd
from pathlib import Path

project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "raw" / "health"
output_folder = project_folder / "data" / "processed" / "integrated"
output_folder.mkdir(parents=True, exist_ok=True)

tract_file = data_folder / "PLACES__Census_Tract_Data_(GIS_Friendly_Format),_2023_release_20260112.csv"

# Kansas City, MO-KS Metro area (14 counties: 9 in Missouri and 5 in Kansas)

kc_metro_counties = {
    "29013": "Bates, MO",
    "29025": "Caldwell, MO",
    "29037": "Cass, MO",
    "29047": "Clay, MO",
    "29049": "Clinton, MO",
    "29095": "Jackson, MO",
    "29107": "Lafayette, MO",
    "29165": "Platte, MO",
    "29177": "Ray, MO",
    "20091": "Johnson, KS",
    "20103": "Leavenworth, KS",
    "20107": "Linn, KS",
    "20121": "Miami, KS",
    "20209": "Wyandotte, KS"
}

health_vars = [
    "OBESITY_CrudePrev",
    "DIABETES_CrudePrev",
    "BPHIGH_CrudePrev"
]

print("=" * 60)
print("FILE:", tract_file.name)
print("=" * 60)

df = pd.read_csv(tract_file, dtype={"CountyFIPS": str})
df["CountyFIPS"] = df["CountyFIPS"].str.zfill(5)

print("\nTotal number of rows in PLACES dataset:", len(df))

# Filter to Kansas City Metro
kc = df[df["CountyFIPS"].isin(kc_metro_counties.keys())].copy()

kc["CountyLabel"] = kc["CountyFIPS"].map(kc_metro_counties)

print("\nTotal number of census tracts in KC metro:", kc["TractFIPS"].nunique())

print("\nTracts per county:")

county_counts = (
    kc.groupby("CountyLabel")["TractFIPS"]
    .nunique()
    .sort_values(ascending=False)
)

for county, count in county_counts.items():
    print(county, ":", count)

counties_found = kc["CountyFIPS"].nunique()

print("\nCounties found vs expected:", counties_found, "/ 14")

missing_counties = (
    set(kc_metro_counties.keys())
    - set(kc["CountyFIPS"].unique())
)

if missing_counties:
    print(
        "WARNING - counties with zero tracts found:",
        [kc_metro_counties[c] for c in missing_counties]
    )
else:
    print("All 14 counties present in the filtered data.")

print("\nMissing values in health shortlist:")

for column in health_vars:
    print(column, ":", kc[column].isnull().sum())

# Save filtered dataset
output_file = output_folder / "kc_metro_tract_data.csv"

keep_cols = [
    "StateAbbr",
    "StateDesc",
    "CountyName",
    "CountyFIPS",
    "TractFIPS",
    "TotalPopulation",
    "Geolocation",
    "CountyLabel"
] + health_vars

kc[keep_cols].to_csv(output_file, index=False)

print("\nFiltered output file saved to:", output_file)