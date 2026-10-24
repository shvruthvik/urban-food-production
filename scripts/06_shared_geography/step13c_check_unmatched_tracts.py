
from pathlib import Path
import pandas as pd

health_file = Path("data/kc_metro_tract_data.csv")
crosswalk_file = Path("data/kc_metro_2010_2020_tract_relationships.csv")

health = pd.read_csv(health_file, dtype=str)
crosswalk = pd.read_csv(crosswalk_file, dtype=str)

# Clean the tract IDs
health_ids = set(
    health["TractFIPS"].str.strip().str.zfill(11)
)

crosswalk["GEOID_TRACT_10"] = (
    crosswalk["GEOID_TRACT_10"].str.strip().str.zfill(11)
)

crosswalk["GEOID_TRACT_20"] = (
    crosswalk["GEOID_TRACT_20"].str.strip().str.zfill(11)
)

ids_2010 = set(crosswalk["GEOID_TRACT_10"].dropna())
ids_2020 = set(crosswalk["GEOID_TRACT_20"].dropna())

# Find project IDs that don't match a 2020 tract ID
unmatched = sorted(health_ids - ids_2020)

print("Project tracts:", len(health_ids))
print("Unmatched against 2020 IDs:", len(unmatched))

# Check whether each unmatched ID appears in the 2010 crosswalk
print("\nUNMATCHED TRACT CHECK")
for tract in unmatched:
    in_2010 = tract in ids_2010

    related_2020 = sorted(
        crosswalk.loc[
            crosswalk["GEOID_TRACT_10"] == tract,
            "GEOID_TRACT_20"
        ].dropna().unique()
    )

    print(
        tract,
        "| in 2010 crosswalk:", in_2010,
        "| related 2020 tracts:", related_2020
    )
