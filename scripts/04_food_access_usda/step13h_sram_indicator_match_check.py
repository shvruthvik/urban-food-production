
import pandas as pd
from pathlib import Path

# --------------------------------------------------
# STEP 1: File paths
# --------------------------------------------------

data_folder = Path("data")

project_file = data_folder / "kc_metro_tract_data.csv"
sram_file = data_folder / "2025-sram-fara-data.xlsx"

# --------------------------------------------------
# STEP 2: Load the project tract IDs
# --------------------------------------------------

project = pd.read_csv(
    project_file,
    dtype={"TractFIPS": str}
)

project["GEOID"] = (
    project["TractFIPS"]
    .astype("string")
    .str.strip()
    .str.zfill(11)
)

project_ids = set(project["GEOID"].dropna())

# --------------------------------------------------
# STEP 3: Load USDA driving-distance data
# --------------------------------------------------

sram = pd.read_excel(
    sram_file,
    sheet_name="Driving Distance Data",
    header=1,
    dtype={"CensusTract20": str}
)

sram["GEOID"] = (
    sram["CensusTract20"]
    .astype("string")
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

candidate_columns = [
    "DD_SRAM_lapop1share",
    "DD_SRAM_LILATracts_1And10",
    "DD_SRAM_LA1and10"
]

for column in candidate_columns:
    sram[column] = pd.to_numeric(
        sram[column],
        errors="coerce"
    )

# --------------------------------------------------
# STEP 4: Filter USDA data to project counties
# --------------------------------------------------

study_counties = {
    ("20", "091"), ("20", "103"), ("20", "107"),
    ("20", "121"), ("20", "209"),
    ("29", "013"), ("29", "025"), ("29", "037"),
    ("29", "047"), ("29", "049"), ("29", "095"),
    ("29", "107"), ("29", "165"), ("29", "177")
}

sram["StateFP"] = sram["GEOID"].str[:2]
sram["CountyFP"] = sram["GEOID"].str[2:5]

sram = sram[
    sram.apply(
        lambda row: (
            row["StateFP"], row["CountyFP"]
        ) in study_counties,
        axis=1
    )
].copy()

# --------------------------------------------------
# STEP 5: Compare tract IDs
# --------------------------------------------------

sram_ids = set(sram["GEOID"].dropna())

matched_ids = project_ids & sram_ids
project_only_ids = project_ids - sram_ids
sram_only_ids = sram_ids - project_ids

print("USDA INDICATOR MATCH CHECK")
print("=" * 50)
print("Project tracts:", len(project_ids))
print("USDA tracts in study counties:", len(sram_ids))
print("Exact ID matches:", len(matched_ids))
print("Project tracts without exact matches:", len(project_only_ids))
print("USDA tracts without exact matches:", len(sram_only_ids))

# --------------------------------------------------
# STEP 6: Summarize candidate indicators
# --------------------------------------------------

matched = sram[sram["GEOID"].isin(matched_ids)].copy()

print("\nINDICATOR SUMMARY FOR EXACT-MATCH TRACTS")
print("=" * 50)

for column in candidate_columns:
    values = matched[column].dropna()

    print(f"\n{column}")
    print("Nonmissing:", len(values))
    print("Missing:", int(matched[column].isna().sum()))

    if len(values):
        print("Minimum:", values.min())
        print("Maximum:", values.max())
        print("Mean:", round(values.mean(), 3))

    if column in [
        "DD_SRAM_LILATracts_1And10",
        "DD_SRAM_LA1and10"
    ]:
        print("Flagged 1:", int((values == 1).sum()))
        print("Flagged 0:", int((values == 0).sum()))

# --------------------------------------------------
# STEP 7: Save unmatched project IDs for review
# --------------------------------------------------

output_file = data_folder / "sram_project_unmatched_ids.csv"

pd.DataFrame({
    "GEOID": sorted(project_only_ids)
}).to_csv(output_file, index=False)

print("\nSaved unmatched IDs to:", output_file)
print("\nCheck complete. No original data was modified.")
