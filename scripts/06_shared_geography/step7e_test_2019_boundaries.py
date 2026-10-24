
from pathlib import Path
import pandas as pd
import geopandas as gpd

# Your project folder
project_folder = Path.cwd()
data_folder = project_folder / "data"

# Search for the extracted 2019 shapefiles
kansas_files = list(project_folder.rglob("tl_2019_20_tract.shp"))
missouri_files = list(project_folder.rglob("tl_2019_29_tract.shp"))

print("Project folder:", project_folder)
print("Kansas files found:", kansas_files)
print("Missouri files found:", missouri_files)

if not kansas_files or not missouri_files:
    print("\nCould not find both shapefiles.")
    print("Check that the folders are inside the project directory.")
else:
    data = pd.read_csv(
        data_folder / "kc_metro_combined_health_socioeconomic.csv",
        dtype=str
    )
    data["TractFIPS"] = data["TractFIPS"].str.strip()

    kansas = gpd.read_file(kansas_files[0])
    missouri = gpd.read_file(missouri_files[0])

    kansas["GEOID"] = kansas["GEOID"].astype(str).str.strip()
    missouri["GEOID"] = missouri["GEOID"].astype(str).str.strip()

    boundary_ids = set(kansas["GEOID"]) | set(missouri["GEOID"])
    study_ids = set(data["TractFIPS"])

    matched = study_ids & boundary_ids
    missing = sorted(study_ids - boundary_ids)

    print("\nStudy tracts:", len(study_ids))
    print("Matched to 2019 boundaries:", len(matched))
    print("Unmatched:", len(missing))
    print("Example unmatched IDs:", missing[:10])
