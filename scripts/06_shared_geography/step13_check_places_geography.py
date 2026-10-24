
from pathlib import Path
import pandas as pd
import geopandas as gpd

# --------------------------------------------------
# STEP 1: Set the file paths
# --------------------------------------------------

health_file = Path("data/kc_metro_tract_data.csv")
combined_file = Path("data/kc_metro_combined_health_socioeconomic.csv")
geojson_file = Path("data/kc_metro_tracts_with_data.geojson")

# --------------------------------------------------
# STEP 2: Check which files exist
# --------------------------------------------------

for file in [health_file, combined_file, geojson_file]:
    print(f"{file}: {'FOUND' if file.exists() else 'NOT FOUND'}")

if not health_file.exists():
    raise FileNotFoundError(health_file)

# --------------------------------------------------
# STEP 3: Load the health dataset
# --------------------------------------------------

health = pd.read_csv(health_file, dtype=str)

print("\nHEALTH DATASET")
print("=" * 45)
print("Rows:", len(health))
print("Columns:", len(health.columns))
print("Column names:", list(health.columns))

# --------------------------------------------------
# STEP 4: Find the tract ID column
# --------------------------------------------------

possible_ids = [
    "LocationID",
    "GEOID",
    "TractFIPS",
    "GEOID_TRACT",
    "GeographicID"
]

id_column = next(
    (column for column in possible_ids if column in health.columns),
    None
)

if id_column is None:
    print("\nCould not identify the tract ID column automatically.")
    print("Please send me the column names printed above.")
    raise SystemExit

health_ids = set(
    health[id_column]
    .dropna()
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

print("\nTract ID column:", id_column)
print("Unique health tract IDs:", len(health_ids))

# --------------------------------------------------
# STEP 5: Compare with the existing project GeoJSON
# --------------------------------------------------

if geojson_file.exists():
    geo = gpd.read_file(geojson_file)

    print("\nGEOJSON COLUMNS:", list(geo.columns))

    geo_id_column = next(
        (column for column in ["GEOID", "GEOID10", "GEOID20"]
         if column in geo.columns),
        None
    )

    if geo_id_column is None:
        print("Could not identify the GeoJSON tract ID column.")
    else:
        geo_ids = set(
            geo[geo_id_column]
            .dropna()
            .astype(str)
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.zfill(11)
        )

        print("\nHEALTH VS PROJECT GEOJSON")
        print("Health unique IDs:", len(health_ids))
        print("GeoJSON unique IDs:", len(geo_ids))
        print("Matching IDs:", len(health_ids & geo_ids))
        print("Health IDs not in GeoJSON:", len(health_ids - geo_ids))
        print("GeoJSON IDs not in health:", len(geo_ids - health_ids))

# --------------------------------------------------
# STEP 6: Compare with the combined dataset
# --------------------------------------------------

if combined_file.exists():
    combined = pd.read_csv(combined_file, dtype=str)

    print("\nCOMBINED DATASET")
    print("Rows:", len(combined))
    print("Columns:", list(combined.columns))

print("\nHealth geography audit complete.")
