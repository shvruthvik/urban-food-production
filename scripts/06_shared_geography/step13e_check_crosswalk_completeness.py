
import pandas as pd
from pathlib import Path

folder = Path("data/tract_boundaries")

files = [
    folder / "tab20_tract20_tract10_st20.txt",
    folder / "tab20_tract20_tract10_st29.txt"
]

study_counties = {
    ("20", "091"), ("20", "103"), ("20", "107"),
    ("20", "121"), ("20", "209"),
    ("29", "013"), ("29", "025"), ("29", "037"),
    ("29", "047"), ("29", "049"), ("29", "095"),
    ("29", "107"), ("29", "165"), ("29", "177")
}

frames = []

for file in files:
    if not file.exists():
        raise FileNotFoundError(f"Missing file: {file}")

    df = pd.read_csv(file, sep="|", dtype=str)
    frames.append(df)

all_links = pd.concat(frames, ignore_index=True)

for column in ["GEOID_TRACT_20", "GEOID_TRACT_10"]:
    all_links[column] = (
        all_links[column].astype(str).str.strip().str.zfill(11)
    )

all_links["STATEFP20"] = all_links["GEOID_TRACT_20"].str[:2]
all_links["COUNTYFP20"] = all_links["GEOID_TRACT_20"].str[2:5]

# All links whose 2020 tract is in the study counties
inside_links = all_links[
    all_links.apply(
        lambda row: (row["STATEFP20"], row["COUNTYFP20"])
        in study_counties,
        axis=1
    )
].copy()

# Find old tracts linked to study-area 2020 tracts
old_ids_in_study = set(inside_links["GEOID_TRACT_10"])

# For those old tracts, retain every relationship,
# including links to 2020 tracts outside the study counties
all_links_for_those_old_tracts = all_links[
    all_links["GEOID_TRACT_10"].isin(old_ids_in_study)
].copy()

outside_links = all_links_for_those_old_tracts[
    ~all_links_for_those_old_tracts.apply(
        lambda row: (row["STATEFP20"], row["COUNTYFP20"])
        in study_counties,
        axis=1
    )
].copy()

print("CROSSWALK COMPLETENESS CHECK")
print("=" * 45)
print("All source relationship rows:", len(all_links))
print("Relationships inside study counties:", len(inside_links))
print("Distinct 2010 tracts linked to study counties:",
      len(old_ids_in_study))
print("Relationships to 2020 tracts outside study counties:",
      len(outside_links))
print("Distinct 2010 tracts with outside links:",
      outside_links["GEOID_TRACT_10"].nunique())

if len(outside_links) > 0:
    print("\nExamples of outside relationships:")
    print(
        outside_links[
            ["GEOID_TRACT_10", "GEOID_TRACT_20"]
        ].head(15).to_string(index=False)
    )
else:
    print("\nNo outside relationships found for these 2010 tracts.")

# Inspect every relationship for the four affected 2010 tracts

affected_ids = sorted(
    outside_links["GEOID_TRACT_10"].unique()
)

print("\nDETAILS FOR AFFECTED 2010 TRACTS")
print("=" * 55)

for tract_id in affected_ids:
    print(f"\n2010 tract: {tract_id}")

    details = all_links[
        all_links["GEOID_TRACT_10"] == tract_id
    ].copy()

    details["2020_State"] = details["GEOID_TRACT_20"].str[:2]
    details["2020_County"] = details["GEOID_TRACT_20"].str[2:5]

    details["In_Study_Area"] = details.apply(
        lambda row: (
            row["2020_State"], row["2020_County"]
        ) in study_counties,
        axis=1
    )

    print(
        details[
            [
                "GEOID_TRACT_10",
                "GEOID_TRACT_20",
                "2020_County",
                "In_Study_Area"
            ]
        ].to_string(index=False)
    )