
from pathlib import Path
import zipfile
import geopandas as gpd
import pyogrio

# Project and source file locations
project_folder = Path.home() / "Downloads" / "Urban food Production"
zip_file = Path.home() / "Downloads" / "Cadastre.gdb.zip"
output_folder = project_folder / "outputs" / "parcels"

# Create the output folder if it does not exist
output_folder.mkdir(parents=True, exist_ok=True)

print("Checking parcel ZIP file...")

if not zip_file.exists():
    raise FileNotFoundError(f"ZIP file not found: {zip_file}")

# Inspect the ZIP without extracting it
with zipfile.ZipFile(zip_file, "r") as archive:
    file_names = archive.namelist()

print("ZIP file found.")
print("Number of files inside ZIP:", len(file_names))

# List the GIS layers available in the ZIP
layers = pyogrio.list_layers(f"zip://{zip_file}")

print("\nAvailable GIS layers:")
for layer in layers:
    print(layer)

# Save the layer list for the project report
with open(output_folder / "parcel_layer_inventory.txt", "w") as file:
    file.write("Kansas City Parcel Geodatabase - Layer Inventory\n\n")
    for layer in layers:
        file.write(str(layer) + "\n")

print("\nLayer inventory saved.")

# Find the parcel layer
layer_names = [str(layer[0]) for layer in layers]
parcel_layer = next(
    (name for name in layer_names if name.lower() == "parcels"),
    None
)

if parcel_layer is None:
    print("A layer named 'Parcels' was not found.")
    print("Review parcel_layer_inventory.txt to identify the correct layer.")
else:
    print("\nReading parcel layer:", parcel_layer)

    parcels = gpd.read_file(
        f"zip://{zip_file}",
        layer=parcel_layer,
        engine="pyogrio"
    )

    print("\nParcel layer inspection")
    print("-----------------------")
    print("Number of records:", len(parcels))
    print("Number of columns:", len(parcels.columns))
    print("Coordinate reference system:", parcels.crs)
    print("Geometry types:")
    print(parcels.geom_type.value_counts().to_string())

    print("\nColumn names:")
    print(parcels.columns.tolist())

    print("\nFirst five rows:")
    print(parcels.head().to_string())

    print("\nGeographic bounds:")
    print(parcels.total_bounds)

    # Save a field inventory
    field_inventory = parcels.dtypes.astype(str).reset_index()
    field_inventory.columns = ["Field", "DataType"]
    field_inventory.to_csv(
        output_folder / "parcel_field_inventory.csv",
        index=False
    )

    # Save a small sample, not the full parcel dataset
    parcels.head(100).drop(columns="geometry").to_csv(
        output_folder / "parcel_sample_100.csv",
        index=False
    )

    print("\nSaved outputs:")
    print("parcel_field_inventory.csv")
    print("parcel_sample_100.csv")

