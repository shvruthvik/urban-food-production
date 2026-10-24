
from pathlib import Path

base = Path("data/tract_boundaries")

print("Searching inside:", base.resolve())
print("Folder exists:", base.exists())

print("\nFolders found:")
for path in base.rglob("*"):
    if path.is_dir():
        print(path)

print("\nShapefiles found:")
for path in base.rglob("*.shp"):
    print(path)

print("\nZIP files found:")
for path in base.rglob("*.zip"):
    print(path)
