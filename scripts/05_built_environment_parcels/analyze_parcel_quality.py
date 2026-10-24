
from pathlib import Path
import geopandas as gpd
import pandas as pd
import pyogrio

# File locations
project_folder = Path.home() / "Downloads" / "Urban food Production"
zip_file = Path.home() / "Downloads" / "Cadastre.gdb.zip"
output_folder = project_folder / "outputs" / "parcels"

output_folder.mkdir(parents=True, exist_ok=True)

print("Reading parcel data...")

parcels = gpd.read_file(
    f"zip://{zip_file}",
    layer="Parcels",
    engine="pyogrio"
)

print("\n1. BASIC DATA CHECK")
print("Total records:", len(parcels))
print("Unique KIVAPIN values:", parcels["KIVAPIN"].nunique())
print("Missing KIVAPIN:", parcels["KIVAPIN"].isna().sum())
print("Duplicate KIVAPIN rows:", parcels["KIVAPIN"].duplicated().sum())
print("Missing geometry:", parcels.geometry.isna().sum())
print("Empty geometry:", parcels.geometry.is_empty.sum())
print("Invalid geometry:", (~parcels.geometry.is_valid).sum())

# Check land-use codes
print("\n2. LAND-USE CODE CHECK")
print("Missing land-use codes:", parcels["LANDUSECODE"].isna().sum())

land_use_counts = (
    parcels["LANDUSECODE"]
    .value_counts(dropna=False)
    .rename_axis("LANDUSECODE")
    .reset_index(name="ParcelCount")
)

print("\nMost common land-use codes:")
print(land_use_counts.head(15).to_string(index=False))

land_use_counts.to_csv(
    output_folder / "parcel_landuse_code_counts.csv",
    index=False
)

# Check improvement values
print("\n3. IMPROVEMENT VALUE CHECK")

improvement = pd.to_numeric(
    parcels["ASSESSED_IMPROVE_VALUE"],
    errors="coerce"
)

print("Missing improvement values:", improvement.isna().sum())
print("Zero improvement values:", (improvement == 0).sum())
print("Positive improvement values:", (improvement > 0).sum())
print("Negative improvement values:", (improvement < 0).sum())

# Check parcel areas using polygon geometry
print("\n4. PARCEL AREA CHECK")

area = parcels.geometry.area

print("Missing geometry-based area:", area.isna().sum())
print("Zero-area or negative-area geometries:", (area <= 0).sum())
print("Area percentiles (square feet):")
print(
    area.quantile([0, 0.25, 0.50, 0.75, 0.90, 0.95, 0.99, 1.0])
    .to_string()
)

# Save a field inventory with missing-value counts
field_summary = pd.DataFrame({
    "Field": parcels.columns,
    "DataType": [str(parcels[column].dtype) for column in parcels.columns],
    "MissingValues": [parcels[column].isna().sum() for column in parcels.columns],
    "UniqueValues": [
        parcels[column].nunique(dropna=True)
        for column in parcels.columns
    ]
})

field_summary.to_csv(
    output_folder / "parcel_data_quality_by_field.csv",
    index=False
)

# Save an overall summary for presentation and documentation
summary = [
    ("Total parcel records", len(parcels)),
    ("Unique KIVAPIN values", parcels["KIVAPIN"].nunique()),
    ("Missing KIVAPIN", parcels["KIVAPIN"].isna().sum()),
    ("Duplicate KIVAPIN rows", parcels["KIVAPIN"].duplicated().sum()),
    ("Missing geometry", parcels.geometry.isna().sum()),
    ("Empty geometry", parcels.geometry.is_empty.sum()),
    ("Invalid geometry", (~parcels.geometry.is_valid).sum()),
    ("Missing land-use code", parcels["LANDUSECODE"].isna().sum()),
    ("Missing improvement value", improvement.isna().sum()),
    ("Zero improvement value", (improvement == 0).sum()),
]

pd.DataFrame(summary, columns=["Check", "Result"]).to_csv(
    output_folder / "parcel_quality_summary.csv",
    index=False
)

print("\n5. REPORTS SAVED")
print("parcel_landuse_code_counts.csv")
print("parcel_data_quality_by_field.csv")
print("parcel_quality_summary.csv")
print("\nParcel quality inspection completed.")
