
from pathlib import Path
import zipfile

# Folder containing the downloaded ZIP files
data_folder = Path("data")
boundary_folder = data_folder / "tract_boundaries"

# The two downloaded files
zip_files = [
    ("tl_2023_20_tract.zip", "kansas"),
    ("tl_2023_29_tract.zip", "missouri")
]

for zip_name, state_name in zip_files:
    zip_path = boundary_folder / zip_name
    output_folder = boundary_folder / state_name

    # Check whether the ZIP file exists
    if not zip_path.exists():
        print("File not found:", zip_path)
        continue

    # Create an output folder for the extracted files
    output_folder.mkdir(parents=True, exist_ok=True)

    # Extract the ZIP contents
    with zipfile.ZipFile(zip_path, "r") as zip_file:
        zip_file.extractall(output_folder)

    print("\nExtracted:", state_name)

    # Find the shapefile
    shapefiles = list(output_folder.glob("*.shp"))

    for shapefile in shapefiles:
        print("Shapefile:", shapefile.name)

print("\nBoundary extraction check complete.")
