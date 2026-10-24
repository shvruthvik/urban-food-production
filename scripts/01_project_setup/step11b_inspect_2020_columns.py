
from pathlib import Path
import geopandas as gpd

base = Path("data/tract_boundaries")

# Find the 2020 tract shapefiles
ks_files = list(base.rglob("tl_2020_20_tract20.shp"))
mo_files = list(base.rglob("tl_2020_29_tract20.shp"))

print("Kansas shapefiles found:", ks_files)
print("Missouri shapefiles found:", mo_files)

# Inspect the Kansas shapefile
if ks_files:
    ks = gpd.read_file(ks_files[0])
    print("\nKANSAS COLUMNS:")
    print(ks.columns.tolist())
    print("\nKANSAS SAMPLE:")
    print(ks.head(2).to_string())

# Inspect the Missouri shapefile
if mo_files:
    mo = gpd.read_file(mo_files[0])
    print("\nMISSOURI COLUMNS:")
    print(mo.columns.tolist())
    print("\nMISSOURI SAMPLE:")
    print(mo.head(2).to_string())
