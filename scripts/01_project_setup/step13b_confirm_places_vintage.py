
from pathlib import Path
import pandas as pd

health_file = Path("data/kc_metro_tract_data.csv")
crosswalk_file = Path("data/kc_metro_2010_2020_tract_relationships.csv")

if not health_file.exists() or not crosswalk_file.exists():
    print("A required file is missing.")
    print("Health file found:", health_file.exists())
    print("Crosswalk file found:", crosswalk_file.exists())
    raise SystemExit

health = pd.read_csv(health_file, dtype=str)
crosswalk = pd.read_csv(crosswalk_file, dtype=str)

health_ids = set(health["TractFIPS"].str.strip().str.zfill(11))
tracts_2010 = set(crosswalk["GEOID_TRACT_10"].dropna().str.strip().str.zfill(11))
tracts_2020 = set(crosswalk["GEOID_TRACT_20"].dropna().str.strip().str.zfill(11))

print("CDC PLACES unique tract IDs:", len(health_ids))
print("IDs found in 2010 tract list:", len(health_ids & tracts_2010))
print("IDs not found in 2010 tract list:", len(health_ids - tracts_2010))
print("IDs found in 2020 tract list:", len(health_ids & tracts_2020))
print("IDs not found in 2020 tract list:", len(health_ids - tracts_2020))
