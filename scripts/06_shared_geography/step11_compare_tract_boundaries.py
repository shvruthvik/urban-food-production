
from pathlib import Path
import pandas as pd
import geopandas as gpd

# --------------------------------------------------
# STEP 1: Set up file paths
# --------------------------------------------------

base = Path("data/tract_boundaries")

project_file = Path("data/kc_metro_tracts_with_data.geojson")
sram_file = Path("data/sram_kc_metro_2020_tracts.csv")

output_folder = Path("data")
output_folder.mkdir(exist_ok=True)

# Find the 2020 census tract shapefiles
ks_files = list(base.rglob("tl_2020_20_tract20.shp"))
mo_files = list(base.rglob("tl_2020_29_tract20.shp"))

if not ks_files:
    raise FileNotFoundError(
        "Kansas 2020 shapefile was not found."
    )

if not mo_files:
    raise FileNotFoundError(
        "Missouri 2020 shapefile was not found."
    )

if not project_file.exists():
    raise FileNotFoundError(
        f"Project GeoJSON was not found: {project_file}"
    )

if not sram_file.exists():
    raise FileNotFoundError(
        f"USDA SRAM CSV was not found: {sram_file}"
    )

print("Loading Kansas 2020 boundaries...")
ks = gpd.read_file(ks_files[0])

print("Loading Missouri 2020 boundaries...")
mo = gpd.read_file(mo_files[0])

# --------------------------------------------------
# STEP 2: Standardize the boundary column names
# --------------------------------------------------

required_columns = [
    "STATEFP20",
    "COUNTYFP20",
    "GEOID20"
]

for state_name, frame in [("Kansas", ks), ("Missouri", mo)]:
    missing_columns = [
        col for col in required_columns
        if col not in frame.columns
    ]

    if missing_columns:
        raise ValueError(
            f"{state_name} shapefile is missing columns: "
            f"{missing_columns}"
        )

ks = ks.rename(columns={
    "STATEFP20": "STATEFP",
    "COUNTYFP20": "COUNTYFP",
    "GEOID20": "GEOID"
})

mo = mo.rename(columns={
    "STATEFP20": "STATEFP",
    "COUNTYFP20": "COUNTYFP",
    "GEOID20": "GEOID"
})

# --------------------------------------------------
# STEP 3: Combine the Kansas and Missouri boundaries
# --------------------------------------------------

tracts = pd.concat(
    [
        ks[["STATEFP", "COUNTYFP", "GEOID"]],
        mo[["STATEFP", "COUNTYFP", "GEOID"]]
    ],
    ignore_index=True
)

for col in ["STATEFP", "COUNTYFP", "GEOID"]:
    tracts[col] = tracts[col].astype(str).str.strip()

tracts["GEOID"] = tracts["GEOID"].str.zfill(11)

# The 14 study-area counties, identified by state and county FIPS
study_counties = {
    ("20", "091"),  # Johnson, Kansas
    ("20", "103"),  # Leavenworth, Kansas
    ("20", "107"),  # Linn, Kansas
    ("20", "121"),  # Miami, Kansas
    ("20", "209"),  # Wyandotte, Kansas
    ("29", "013"),  # Bates, Missouri
    ("29", "025"),  # Caldwell, Missouri
    ("29", "037"),  # Cass, Missouri
    ("29", "047"),  # Clay, Missouri
    ("29", "049"),  # Clinton, Missouri
    ("29", "095"),  # Jackson, Missouri
    ("29", "107"),  # Lafayette, Missouri
    ("29", "165"),  # Platte, Missouri
    ("29", "177")   # Ray, Missouri
}

tracts = tracts[
    tracts.apply(
        lambda row: (row["STATEFP"], row["COUNTYFP"])
        in study_counties,
        axis=1
    )
].copy()

tracts = tracts.drop_duplicates(subset="GEOID")

boundary_ids = set(tracts["GEOID"])

# --------------------------------------------------
# STEP 4: Load the existing project tract IDs
# --------------------------------------------------

print("Loading existing project data...")
project = gpd.read_file(project_file)

if "GEOID" not in project.columns:
    raise ValueError(
        "The project GeoJSON does not contain a GEOID column."
    )

project["GEOID"] = (
    project["GEOID"].astype(str).str.strip().str.zfill(11)
)

project_ids = set(project["GEOID"].dropna().unique())

# --------------------------------------------------
# STEP 5: Load the USDA SRAM tract IDs
# --------------------------------------------------

print("Loading USDA SRAM data...")
sram = pd.read_csv(
    sram_file,
    dtype={"CensusTract20": str}
)

if "CensusTract20" not in sram.columns:
    raise ValueError(
        "The USDA SRAM CSV does not contain CensusTract20."
    )

sram["GEOID"] = (
    sram["CensusTract20"]
    .astype(str)
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

sram_ids = set(sram["GEOID"].dropna().unique())

# --------------------------------------------------
# STEP 6: Compare the three sets of tract IDs
# --------------------------------------------------

print("\n" + "=" * 55)
print("2020 CENSUS TRACT GEOGRAPHY COMPARISON")
print("=" * 55)

print(f"2020 boundary tracts in study counties: {len(boundary_ids)}")
print(f"Existing project tracts (2019 data): {len(project_ids)}")
print(f"USDA SRAM tract IDs: {len(sram_ids)}")

print("\n2020 boundaries vs existing project:")
print(f"Matching IDs: {len(boundary_ids & project_ids)}")
print(f"Boundary IDs not in project: {len(boundary_ids - project_ids)}")
print(f"Project IDs not in boundaries: {len(project_ids - boundary_ids)}")

print("\n2020 boundaries vs USDA SRAM:")
print(f"Matching IDs: {len(boundary_ids & sram_ids)}")
print(f"Boundary IDs not in SRAM: {len(boundary_ids - sram_ids)}")
print(f"SRAM IDs not in boundaries: {len(sram_ids - boundary_ids)}")

print("\nExisting project vs USDA SRAM:")
print(f"Matching IDs: {len(project_ids & sram_ids)}")
print(f"Project IDs not in SRAM: {len(project_ids - sram_ids)}")
print(f"SRAM IDs not in project: {len(sram_ids - project_ids)}")

# --------------------------------------------------
# STEP 7: Save a detailed ID comparison file
# --------------------------------------------------

all_ids = sorted(boundary_ids | project_ids | sram_ids)

comparison = pd.DataFrame({
    "GEOID": all_ids
})

comparison["In_2020_Boundaries"] = (
    comparison["GEOID"].isin(boundary_ids)
)

comparison["In_Existing_Project"] = (
    comparison["GEOID"].isin(project_ids)
)

comparison["In_USDA_SRAM"] = (
    comparison["GEOID"].isin(sram_ids)
)

comparison.to_csv(
    output_folder / "step11_tract_id_comparison.csv",
    index=False
)

# --------------------------------------------------
# STEP 8: Save a readable report
# --------------------------------------------------

report_lines = [
    "2020 CENSUS TRACT GEOGRAPHY COMPARISON",
    "=" * 45,
    f"2020 boundary tracts: {len(boundary_ids)}",
    f"Existing project tracts: {len(project_ids)}",
    f"USDA SRAM tract IDs: {len(sram_ids)}",
    "",
    "2020 boundaries vs existing project:",
    f"Matching IDs: {len(boundary_ids & project_ids)}",
    f"Boundary IDs not in project: {len(boundary_ids - project_ids)}",
    f"Project IDs not in boundaries: {len(project_ids - boundary_ids)}",
    "",
    "2020 boundaries vs USDA SRAM:",
    f"Matching IDs: {len(boundary_ids & sram_ids)}",
    f"Boundary IDs not in SRAM: {len(boundary_ids - sram_ids)}",
    f"SRAM IDs not in boundaries: {len(sram_ids - boundary_ids)}",
    "",
    "Existing project vs USDA SRAM:",
    f"Matching IDs: {len(project_ids & sram_ids)}",
    f"Project IDs not in SRAM: {len(project_ids - sram_ids)}",
    f"SRAM IDs not in project: {len(sram_ids - project_ids)}",
    "",
    "Important: matching GEOIDs do not by themselves prove",
    "that two datasets use identical geographic boundaries."
]

report_path = output_folder / "step11_tract_id_comparison_report.txt"

report_path.write_text(
    "\n".join(report_lines),
    encoding="utf-8"
)

print("\nFiles saved:")
print(output_folder / "step11_tract_id_comparison.csv")
print(report_path)

print("\nComparison completed.")
