
from pathlib import Path
from zipfile import ZipFile
import pandas as pd
import geopandas as gpd

gtfs_file = Path("data/kcata_gtfs_october2026_20261001.zip")
tract_file = Path("data/kc_metro_tracts_with_data.geojson")

if not gtfs_file.exists() or not tract_file.exists():
    print("A required file is missing.")
    print("GTFS found:", gtfs_file.exists())
    print("Tract GeoJSON found:", tract_file.exists())
    raise SystemExit

# Read transit stops from the ZIP
with ZipFile(gtfs_file, "r") as archive:
    stops = pd.read_csv(archive.open("stops.txt"))

# Read existing project census-tract boundaries
tracts = gpd.read_file(tract_file)

# Make sure both layers use a compatible coordinate system
stop_points = gpd.GeoDataFrame(
    stops,
    geometry=gpd.points_from_xy(
        stops["stop_lon"], stops["stop_lat"]
    ),
    crs="EPSG:4326"
)

if tracts.crs is None:
    print("The tract GeoJSON has no declared CRS.")
    print("We need to inspect its coordinate system before continuing.")
    raise SystemExit

stop_points = stop_points.to_crs(tracts.crs)

# Count stops that fall inside project census tracts
matched = gpd.sjoin(
    stop_points,
    tracts[["GEOID", "CountyName", "geometry"]],
    how="left",
    predicate="within"
)

matched_stops = matched[matched["index_right"].notna()]
unmatched_stops = matched[matched["index_right"].isna()]

print("TRANSIT COVERAGE CHECK")
print("=" * 40)
print("Project census tracts:", len(tracts))
print("Transit stop records:", len(stop_points))
print("Stops inside project tracts:", len(matched_stops))
print("Stops outside project tracts:", len(unmatched_stops))
print("Unique project tracts with stops:",
      matched_stops["GEOID"].nunique())

print("\nSTOPS BY COUNTY")
print(
    matched_stops.groupby("CountyName")
    .size()
    .sort_values(ascending=False)
    .to_string()
)

print("\nPROJECT COUNTIES WITH NO MATCHED STOPS")
project_counties = set(tracts["CountyName"].dropna().unique())
covered_counties = set(
    matched_stops["CountyName"].dropna().unique()
)

for county in sorted(project_counties - covered_counties):
    print(county)

print("\nCoverage check complete.")
print("No input files were modified.")

