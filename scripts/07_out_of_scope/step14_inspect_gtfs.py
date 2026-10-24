
from pathlib import Path
from zipfile import ZipFile

# Find the GTFS ZIP file
gtfs_file = Path("data/kcata_gtfs_october2026_20261001.zip")

if not gtfs_file.exists():
    print("GTFS ZIP file not found.")
    raise SystemExit

# Open the ZIP without extracting its contents
with ZipFile(gtfs_file, "r") as archive:
    files = archive.namelist()

    print("GTFS ZIP file:", gtfs_file.name)
    print("Number of files:", len(files))
    print("\nFiles inside the archive:")
    
    for file in files:
        print(file)

    # Check for important GTFS tables
    required_files = [
        "agency.txt",
        "routes.txt",
        "stops.txt",
        "trips.txt",
        "stop_times.txt",
        "calendar.txt",
        "calendar_dates.txt"
    ]

    print("\nGTFS TABLE CHECK")
    for required in required_files:
        matches = [
            name for name in files
            if name == required or name.endswith("/" + required)
        ]

        status = "FOUND" if matches else "NOT FOUND"
        print(f"{required}: {status}")

print("\nInspection complete. No files were extracted or changed.")
