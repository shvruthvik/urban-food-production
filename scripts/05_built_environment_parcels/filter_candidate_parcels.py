
from pathlib import Path
import geopandas as gpd
import pandas as pd

# Project and file locations
project_folder = Path(__file__).resolve().parents[2]
zip_file = Path.home() / "Downloads" / "Cadastre.gdb.zip"
output_folder = project_folder / "data" / "processed" / "built_environment"

output_folder.mkdir(parents=True, exist_ok=True)

print("Reading KCMO parcel data...")

parcels = gpd.read_file(
    f"zip://{zip_file}",
    layer="Parcels",
    engine="pyogrio"
)

# Convert land-use codes to numeric values
parcels["LANDUSECODE"] = pd.to_numeric(
    parcels["LANDUSECODE"], errors="coerce"
)

# Keep the two officially classified vacant-land categories
candidates = parcels[
    parcels["LANDUSECODE"].isin([9500, 9600])
].copy()

print("Candidate parcel records:", len(candidates))

# Calculate parcel area from the polygon geometry
# The source CRS uses US survey feet
candidates["Area_SqFt"] = candidates.geometry.area

# Add a geometry quality flag
candidates["GeometryValid"] = (
    candidates.geometry.notna()
    & ~candidates.geometry.is_empty
    & candidates.geometry.is_valid
)

# Keep only useful attribute fields in the CSV
columns_to_keep = [
    "KIVAPIN",
    "APN",
    "ADDRESS",
    "LANDUSECODE",
    "ASSESSED_LAND_VALUE",
    "ASSESSED_IMPROVE_VALUE",
    "Area_SqFt",
    "GeometryValid",
    "geometry"
]

candidates = candidates[columns_to_keep]

# Export a CSV without geometry; geometry will be exported separately
csv_output = output_folder / "kcmo_vacant_candidate_parcels.csv"

candidates.drop(columns="geometry").to_csv(
    csv_output,
    index=False
)

# Export parcel polygons to GeoJSON for future mapping
# Reproject to longitude/latitude for broad GIS compatibility
geojson_output = output_folder / "kcmo_vacant_candidate_parcels.geojson"

candidates.to_crs("EPSG:4326").to_file(
    geojson_output,
    driver="GeoJSON",
    engine="pyogrio"
)

# Print summary by official land-use code
summary = (
    candidates.groupby("LANDUSECODE")
    .agg(
        ParcelRecords=("LANDUSECODE", "size"),
        ValidGeometry=("GeometryValid", "sum"),
        MeanArea_SqFt=("Area_SqFt", "mean"),
        MedianArea_SqFt=("Area_SqFt", "median")
    )
    .reset_index()
)

print("\nCandidate summary:")
print(summary.to_string(index=False))

print("\nSaved files:")
print(csv_output)
print(geojson_output)

print("\nImportant:")
print("These are classification-based candidates, not confirmed suitable sites.")
print("The exported GeoJSON retains parcel boundaries for spatial analysis.")
