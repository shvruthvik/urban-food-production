
from pathlib import Path
import geopandas as gpd

project_folder = Path(__file__).resolve().parents[2]

tract_file = project_folder / "data" / "processed" / "integrated" / "kc_metro_tracts_with_data.geojson"
parcel_file = (
    project_folder / "data" / "processed" / "built_environment"
    / "kcmo_vacant_candidate_parcels.geojson"
)
output_folder = project_folder / "data" / "processed" / "built_environment"
output_folder.mkdir(parents=True, exist_ok=True)

print("Reading project census tracts...")
tracts = gpd.read_file(tract_file)

print("Reading candidate parcel boundaries...")
parcels = gpd.read_file(parcel_file)

print("\n1. COORDINATE SYSTEMS")
print("Tract CRS:", tracts.crs)
print("Parcel CRS:", parcels.crs)

if tracts.crs is None or parcels.crs is None:
    raise ValueError("A layer has no CRS. We must resolve that before spatial analysis.")

# Transform both layers to the same projected CRS for area-based analysis.
# Kansas and Missouri State Plane zones are not interchangeable, so use
# a common regional projected CRS rather than assuming the parcel CRS.
analysis_crs = "EPSG:26915"

tracts_projected = tracts.to_crs(analysis_crs)
parcels_projected = parcels.to_crs(analysis_crs)

# Remove empty geometries before calculating intersections
tracts_projected = tracts_projected[
    tracts_projected.geometry.notna()
    & ~tracts_projected.geometry.is_empty
].copy()

parcels_projected = parcels_projected[
    parcels_projected.geometry.notna()
    & ~parcels_projected.geometry.is_empty
].copy()

# Repair invalid geometries for the coverage test only
tracts_projected["geometry"] = tracts_projected.geometry.make_valid()
parcels_projected["geometry"] = parcels_projected.geometry.make_valid()

# Combine tract polygons into one study-area geometry
study_area = tracts_projected.geometry.union_all()

print("\n2. GEOGRAPHIC COVERAGE")
print("Project tract records:", len(tracts_projected))
print("Candidate parcels read:", len(parcels_projected))
print("Project study-area bounds:", tracts_projected.total_bounds)
print("Candidate parcel bounds:", parcels_projected.total_bounds)

# Select parcels that intersect the study-area geometry
inside_mask = parcels_projected.geometry.intersects(study_area)
parcels_inside = parcels_projected.loc[inside_mask].copy()

print("\n3. COVERAGE RESULTS")
print("Candidate parcels intersecting study area:", len(parcels_inside))
print(
    "Candidate parcels outside study area:",
    len(parcels_projected) - len(parcels_inside)
)

# Export the geographic subset in longitude/latitude for mapping
output_geojson = output_folder / "kcmo_candidates_in_study_area.geojson"
parcels_inside.to_crs("EPSG:4326").to_file(
    output_geojson,
    driver="GeoJSON"
)

print("\nSaved:", output_geojson)
print("Note: intersection with the study area does not mean a parcel is suitable.")

