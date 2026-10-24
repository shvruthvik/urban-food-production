
import pandas as pd
import geopandas as gpd
from pathlib import Path

# --------------------------------------------------
# 1. Set up file paths
# --------------------------------------------------

data_folder = Path("data")

sram_file = data_folder / "2025-sram-fara-data.xlsx"
tract_file = data_folder / "kc_metro_tracts_with_data.geojson"

output_comparison = data_folder / "sram_geography_comparison.csv"
output_tracts = data_folder / "sram_kc_metro_2020_tracts.csv"
output_report = data_folder / "sram_geography_audit.txt"

# --------------------------------------------------
# 2. Read the existing project geography
# --------------------------------------------------

tracts = gpd.read_file(tract_file)

print("Existing project rows:", len(tracts))
print("Existing project columns:")
print(tracts.columns.tolist())

required_tract_columns = [
    "GEOID", "StateDesc", "CountyName"
]

for column in required_tract_columns:
    if column not in tracts.columns:
        raise ValueError(
            f"Missing required column in GeoJSON: {column}"
        )

# --------------------------------------------------
# 3. Read the SRAM workbook
# --------------------------------------------------

sheet_name = "GeneralTractCharacteristic Data"

excel = pd.ExcelFile(sram_file)
print("\nSRAM worksheet names:")
print(excel.sheet_names)

if sheet_name not in excel.sheet_names:
    raise ValueError(
        f"Worksheet not found: {sheet_name}"
    )

sram = pd.read_excel(
    sram_file,
    sheet_name=sheet_name,
    header=1
)

print("\nSRAM columns:")
print(sram.columns.tolist())

required_sram_columns = [
    "CensusTract20", "State", "County20"
]

for column in required_sram_columns:
    if column not in sram.columns:
        raise ValueError(
            f"Missing required column in SRAM: {column}"
        )

print("\nTotal rows in SRAM worksheet:", len(sram))

# --------------------------------------------------
# 4. Define helper functions
# --------------------------------------------------

def normalize_name(value):
    """Standardize state and county names for comparison."""
    if pd.isna(value):
        return ""

    name = str(value).strip().casefold()

    # Make 'Johnson County' and 'Johnson' equivalent
    if name.endswith(" county"):
        name = name[:-7].strip()

    return name


def normalize_geoid(value):
    """Convert a tract ID to an 11-character GEOID."""
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()

    # Excel may read integer-like GEOIDs as numbers
    if text.endswith(".0"):
        text = text[:-2]

    # Keep only IDs that contain digits
    if not text.isdigit():
        return pd.NA

    return text.zfill(11)


# --------------------------------------------------
# 5. Normalize the existing project tract data
# --------------------------------------------------

tracts["GEOID_clean"] = tracts["GEOID"].apply(
    normalize_geoid
)

tracts["State_clean"] = tracts["StateDesc"].apply(
    normalize_name
)

tracts["County_clean"] = tracts["CountyName"].apply(
    normalize_name
)

# Identify the 14 study counties using state AND county
study_county_pairs = set(
    zip(
        tracts["State_clean"],
        tracts["County_clean"]
    )
)

existing_ids = set(
    tracts["GEOID_clean"].dropna()
)

# --------------------------------------------------
# 6. Normalize and filter the SRAM data
# --------------------------------------------------

sram["GEOID_clean"] = sram["CensusTract20"].apply(
    normalize_geoid
)

sram["State_clean"] = sram["State"].apply(
    normalize_name
)

sram["County_clean"] = sram["County20"].apply(
    normalize_name
)

sram_county_pairs = list(
    zip(
        sram["State_clean"],
        sram["County_clean"]
    )
)

sram["In_Study_Counties"] = [
    pair in study_county_pairs
    for pair in sram_county_pairs
]

# Keep only the study counties
sram_kc = sram[
    sram["In_Study_Counties"]
].copy()

# Count missing IDs before removing them
missing_sram_ids = int(
    sram_kc["GEOID_clean"].isna().sum()
)

# Remove rows without a usable tract ID
sram_kc = sram_kc[
    sram_kc["GEOID_clean"].notna()
].copy()

sram_ids = set(sram_kc["GEOID_clean"])

print("\nStudy counties identified:", len(study_county_pairs))
print("SRAM rows in study counties:", len(sram_kc))
print("Unique SRAM tract IDs:", len(sram_ids))
print("SRAM rows with missing/invalid IDs:", missing_sram_ids)

print("\nStudy counties found in SRAM:")
found_counties = (
    sram_kc[["State", "County20"]]
    .drop_duplicates()
    .sort_values(["State", "County20"])
)

print(found_counties.to_string(index=False))

# --------------------------------------------------
# 7. Compare the two sets of tract IDs
# --------------------------------------------------
all_ids = sorted(existing_ids | sram_ids)

comparison = pd.DataFrame({
    "Tract_ID": all_ids
})

comparison["In_SRAM_2020"] = (
    comparison["Tract_ID"].isin(sram_ids)
)

comparison["In_Existing_Project"] = (
    comparison["Tract_ID"].isin(existing_ids)
)

def get_match_status(row):
    if row["In_SRAM_2020"] and row["In_Existing_Project"]:
        return "In both datasets"
    elif row["In_SRAM_2020"]:
        return "SRAM only"
    else:
        return "Existing project only"

comparison["Match_Status"] = comparison.apply(
    get_match_status,
    axis=1
)

comparison.to_csv(
    output_comparison,
    index=False
)

# --------------------------------------------------
# 8. Save filtered SRAM records
# --------------------------------------------------

sram_kc.to_csv(
    output_tracts,
    index=False
)

# --------------------------------------------------
# 9. Calculate audit results
# --------------------------------------------------

matched = len(existing_ids & sram_ids)
sram_only = len(sram_ids - existing_ids)
existing_only = len(existing_ids - sram_ids)

duplicate_rows = int(
    sram_kc["GEOID_clean"].duplicated().sum()
)

existing_duplicate_rows = int(
    tracts["GEOID_clean"].duplicated().sum()
)

# --------------------------------------------------
# 9A. Summarize unmatched project tracts by county
# --------------------------------------------------

matched_ids = existing_ids & sram_ids

unmatched_project = tracts[
    ~tracts["GEOID_clean"].isin(sram_ids)
].copy()

county_summary = (
    unmatched_project
    .groupby(["StateDesc", "CountyName"])
    ["GEOID_clean"]
    .nunique()
    .reset_index(name="Unmatched_Tracts")
    .sort_values("Unmatched_Tracts", ascending=False)
)

print("\nUnmatched project tracts by county:")
print(county_summary.to_string(index=False))

county_summary.to_csv(
    data_folder / "unmatched_project_by_county.csv",
    index=False
)

# --------------------------------------------------
# 9B. Summarize USDA-only tracts by county
# --------------------------------------------------

unmatched_sram = sram_kc[
    ~sram_kc["GEOID_clean"].isin(existing_ids)
].copy()

sram_county_summary = (
    unmatched_sram
    .groupby(["State", "County20"])["GEOID_clean"]
    .nunique()
    .reset_index(name="USDA_Only_Tracts")
    .sort_values("USDA_Only_Tracts", ascending=False)
)

print("\nUSDA-only tracts by county:")
print(sram_county_summary.to_string(index=False))

sram_county_summary.to_csv(
    data_folder / "unmatched_usda_by_county.csv",
    index=False
)

# --------------------------------------------------
# 10. Create a readable audit report
# --------------------------------------------------

report = f"""
SRAM GEOGRAPHY AUDIT
====================

Input SRAM worksheet: {sheet_name}

Existing project rows: {len(tracts)}
Unique existing project tract IDs: {len(existing_ids)}

SRAM rows in selected counties: {len(sram_kc)}
Unique SRAM tract IDs: {len(sram_ids)}

Exact tract ID matches: {matched}
SRAM IDs not in existing project: {sram_only}
Existing project IDs not in SRAM: {existing_only}

Missing or invalid SRAM IDs in selected counties:
{missing_sram_ids}

Duplicate SRAM tract ID rows:
{duplicate_rows}

Duplicate existing project GEOID rows:
{existing_duplicate_rows}

Number of state-county pairs in existing study area:
{len(study_county_pairs)}

Important limitations:
1. Exact ID matches do not prove that tract boundaries are identical.
2. The existing project uses 2019 tract geography, while SRAM
   uses 2020 tract geography.
3. This is an exact-ID comparison, not a geographic crosswalk.
4. Do not merge the datasets until geographic compatibility
   has been evaluated.
"""

output_report.write_text(
    report,
    encoding="utf-8"
)

# --------------------------------------------------
# 11. Print the results
# --------------------------------------------------

print(report)

print("Evidence files saved:")
print(output_comparison)
print(output_tracts)
print(output_report)


# --------------------------------------------------
# 12. Inspect the project boundary files
# --------------------------------------------------
boundary_folder = Path("data/tract_boundaries")

boundary_files = [
    boundary_folder / "kansas_2019" / "tl_2019_20_tract" / "tl_2019_20_tract.shp",
    boundary_folder / "missouri_2019" / "tl_2019_29_tract" / "tl_2019_29_tract.shp",
]

print("\nBOUNDARY FILE CHECK")
print("===================")

for boundary_file in boundary_files:
    if boundary_file.exists():
        boundary = gpd.read_file(boundary_file)

        print("\nFile:", boundary_file)
        print("Number of features:", len(boundary))
        print("Unique GEOIDs:", boundary["GEOID"].nunique())
        print("Example GEOIDs:", boundary["GEOID"].head().tolist())
    else:
        print("\nFile not found:", boundary_file)



# 13. Compare project tracts with 2020 Census boundaries

project_file = Path("data/kc_metro_tracts_with_data.geojson")

project = gpd.read_file(project_file)

kansas_2020_file = (
    boundary_folder
    / "kansas_2020"
    / "tl_2020_20_all"
    / "tl_2020_20_tract20.shp"
)

missouri_2020_file = (
    boundary_folder
    / "missouri_2020"
    / "tl_2020_29_all"
    / "tl_2020_29_tract20.shp"
)

kansas_2020 = gpd.read_file(kansas_2020_file)
missouri_2020 = gpd.read_file(missouri_2020_file)

boundary_ids = set(kansas_2020["GEOID20"].astype(str))
boundary_ids.update(missouri_2020["GEOID20"].astype(str))

project_ids = set(project["GEOID"].astype(str))

print("\nPROJECT VS. 2020 CENSUS BOUNDARIES")
print("Unique project GEOIDs:", len(project_ids))
print("Unique 2020 boundary GEOIDs:", len(boundary_ids))
print("Project GEOIDs found in 2020 boundaries:",
      len(project_ids & boundary_ids))
print("Project GEOIDs missing from 2020 boundaries:",
      len(project_ids - boundary_ids))


# 14. Compare project IDs missing from USDA and 2020 boundaries

sram_file = Path("data/sram_geography_comparison.csv")

sram_comparison = pd.read_csv(sram_file, dtype=str)

project_ids = set(project["GEOID"].astype(str))

# IDs found in the project but missing from 2020 boundaries
missing_2020_ids = project_ids - boundary_ids


# IDs found in the project but missing from USDA
missing_sram_ids = set(
    sram_comparison.loc[
        sram_comparison["Match_Status"] == "Existing project only",
        "Tract_ID"
    ].astype(str)
)

print("\nPROJECT-ONLY ID COMPARISON")
print("Missing from 2020 boundaries:", len(missing_2020_ids))
print("Missing from USDA:", len(missing_sram_ids))
print("Missing from both:", len(missing_2020_ids & missing_sram_ids))
print("Missing only from 2020 boundaries:",
      len(missing_2020_ids - missing_sram_ids))
print("Missing only from USDA:",
      len(missing_sram_ids - missing_2020_ids))

print("\nExamples missing from both:")
print(sorted(missing_2020_ids & missing_sram_ids)[:10])


# 15. Summarize the 86 unmatched project tracts by county

missing_ids = sorted(missing_2020_ids & missing_sram_ids)

missing_tracts = project[
    project["GEOID"].astype(str).isin(missing_ids)
].copy()

print("\nUNMATCHED PROJECT TRACTS BY COUNTY")

if "NAME" in missing_tracts.columns:
    print(missing_tracts["NAME"].value_counts().head(20))
else:
    print("County field not found. Available columns:")
    print(missing_tracts.columns.tolist())


# 15. Summarize unmatched project tracts by county

missing_ids = sorted(missing_2020_ids & missing_sram_ids)

missing_tracts = project[
    project["GEOID"].astype(str).isin(missing_ids)
].copy()

print("\nUNMATCHED PROJECT TRACTS BY COUNTY")

county_summary = (
    missing_tracts
    .groupby(["StateDesc", "CountyName"])
    .size()
    .reset_index(name="Unmatched_Tracts")
    .sort_values("Unmatched_Tracts", ascending=False)
)

print(county_summary.to_string(index=False))



# 16. Inspect one unmatched tract

example_id = "20091051802"

print("\nEXAMPLE UNMATCHED TRACT")
print(
    project.loc[
        project["GEOID"].astype(str) == example_id,
        ["GEOID", "StateDesc", "CountyName", "NAME", "NAMELSAD"]
    ].to_string(index=False)
)

# Load the 2019 boundary files
kansas_boundary = gpd.read_file(
    boundary_folder / "kansas_2019" / "tl_2019_20_tract"
    / "tl_2019_20_tract.shp"
)

missouri_boundary = gpd.read_file(
    boundary_folder / "missouri_2019" / "tl_2019_29_tract"
    / "tl_2019_29_tract.shp"
)

boundary_2019_ids = set(kansas_boundary["GEOID"].astype(str))
boundary_2019_ids.update(missouri_boundary["GEOID"].astype(str))

print("\nBOUNDARY ID CHECK")
print("Exists in 2019 boundaries:", example_id in boundary_2019_ids)
print("Exists in 2020 boundaries:", example_id in boundary_ids)

# 17. Compare Johnson County tract IDs across boundary vintages

johnson_2019 = kansas_boundary[
    kansas_boundary["COUNTYFP"] == "091"
]

johnson_2020 = kansas_2020[
    kansas_2020["COUNTYFP20"] == "091"
]

ids_2019 = set(johnson_2019["GEOID"].astype(str))
ids_2020 = set(johnson_2020["GEOID20"].astype(str))

print("\nJOHNSON COUNTY, KANSAS: TRACT ID COMPARISON")
print("2019 boundary tract count:", len(ids_2019))
print("2020 boundary tract count:", len(ids_2020))
print("IDs shared by both vintages:", len(ids_2019 & ids_2020))
print("IDs only in 2019:", len(ids_2019 - ids_2020))
print("IDs only in 2020:", len(ids_2020 - ids_2019))

print("\nExamples of IDs only in 2019:")
print(sorted(ids_2019 - ids_2020)[:15])

print("\nExamples of IDs only in 2020:")
print(sorted(ids_2020 - ids_2019)[:15])

# 18. Compare 2019 and 2020 tract IDs for all study counties

county_pairs = (
    project[["STATEFP", "COUNTYFP", "StateDesc", "CountyName"]]
    .drop_duplicates()
)

summary_rows = []

for _, county in county_pairs.iterrows():
    statefp = str(county["STATEFP"]).zfill(2)
    countyfp = str(county["COUNTYFP"]).zfill(3)
    county_key = statefp + countyfp

    if statefp == "20":
        old_boundary = kansas_boundary
        new_boundary = kansas_2020
    else:
        old_boundary = missouri_boundary
        new_boundary = missouri_2020

    old_ids = set(
        old_boundary.loc[
            old_boundary["GEOID"].astype(str).str.startswith(county_key),
            "GEOID"
        ].astype(str)
    )

    new_ids = set(
        new_boundary.loc[
            new_boundary["GEOID20"].astype(str).str.startswith(county_key),
            "GEOID20"
        ].astype(str)
    )

    summary_rows.append({
        "State": county["StateDesc"],
        "County": county["CountyName"],
        "2019_Tracts": len(old_ids),
        "2020_Tracts": len(new_ids),
        "Shared_IDs": len(old_ids & new_ids),
        "2019_Only": len(old_ids - new_ids),
        "2020_Only": len(new_ids - old_ids)
    })

county_comparison = pd.DataFrame(summary_rows)

print("\n2019 VS. 2020 TRACT ID COMPARISON BY STUDY COUNTY")
print(
    county_comparison
    .sort_values(["State", "County"])
    .to_string(index=False)
)

county_comparison.to_csv(
    "data/tract_vintage_comparison_by_county.csv",
    index=False
)

print("\nSaved: data/tract_vintage_comparison_by_county.csv")
