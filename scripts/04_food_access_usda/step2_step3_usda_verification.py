
"""
Step 2: Verify project tract geography
Step 3: Inventory all USDA LRAM 2019 variables

Run from the project root folder.

Required packages:
pip install pandas openpyxl geopandas
"""

from pathlib import Path
import pandas as pd
import geopandas as gpd


# ==================================================
# STEP 1: Define project file locations
# ==================================================

data_folder = Path("data")

project_geojson = data_folder / "kc_metro_tracts_with_data.geojson"

usda_workbook = data_folder / "FoodAccessResearchAtlasData2019.xlsx"

boundary_folder = data_folder / "tract_boundaries"

# 2019 Census tract boundaries
kansas_2019_file = (
    boundary_folder / "kansas_2019"
    / "tl_2019_20_tract" / "tl_2019_20_tract.shp"
)

missouri_2019_file = (
    boundary_folder / "missouri_2019"
    / "tl_2019_29_tract" / "tl_2019_29_tract.shp"
)

# 2020 Census tract boundaries
kansas_2020_file = (
    boundary_folder / "kansas_2020"
    / "tl_2020_20_all" / "tl_2020_20_tract20.shp"
)

missouri_2020_file = (
    boundary_folder / "missouri_2020"
    / "tl_2020_29_all" / "tl_2020_29_tract20.shp"
)


# Output files
boundary_report_file = data_folder / "LRAM2019_boundary_verification.csv"
geometry_report_file = data_folder / "LRAM2019_geometry_comparison.csv"
variable_inventory_file = data_folder / "LRAM2019_full_variable_inventory.csv"
variable_group_file = data_folder / "LRAM2019_variable_group_summary.csv"


# ==================================================
# STEP 2: Verify the project boundary geography
# ==================================================

print("\n" + "=" * 60)
print("STEP 2: PROJECT BOUNDARY VERIFICATION")
print("=" * 60)


# Check the files required for the geography comparison.

required_boundary_files = [
    project_geojson,
    kansas_2019_file,
    missouri_2019_file,
    kansas_2020_file,
    missouri_2020_file,
]

for file_path in required_boundary_files:
    print(
        "FOUND: " if file_path.exists() else "MISSING: ",
        file_path
    )

if not project_geojson.exists():
    raise FileNotFoundError(
        f"Project geometry file not found: {project_geojson}"
    )


# Load the project's existing tract geometries.

project = gpd.read_file(project_geojson)

if "GEOID" not in project.columns:
    raise ValueError(
        "The project GeoJSON does not contain a GEOID column. "
        "Inspect its columns and update the script."
    )

project["GEOID"] = (
    project["GEOID"].astype(str)
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

project_ids = set(project["GEOID"])

print("\nProject geometry records:", len(project))
print("Unique project GEOIDs:", len(project_ids))
print("Project CRS:", project.crs)


# Function to load and combine the state boundary files.

def load_boundaries(file_1, file_2, id_column):
    """Load two state boundary files and combine their records."""

    if not file_1.exists() or not file_2.exists():
        return None

    first = gpd.read_file(file_1)
    second = gpd.read_file(file_2)

    if id_column not in first.columns:
        raise ValueError(
            f"Column {id_column} not found in {file_1}"
        )

    if id_column not in second.columns:
        raise ValueError(
            f"Column {id_column} not found in {file_2}"
        )

    first = first.rename(columns={id_column: "GEOID"})
    second = second.rename(columns={id_column: "GEOID"})

    combined = pd.concat(
        [first, second],
        ignore_index=True
    )

    combined["GEOID"] = (
        combined["GEOID"].astype(str)
        .str.replace(r"\.0$", "", regex=True)
        .str.zfill(11)
    )

    return gpd.GeoDataFrame(
        combined,
        geometry="geometry",
        crs=first.crs
    )


# Load the 2019 and 2020 boundary datasets.

boundaries_2019 = load_boundaries(
    kansas_2019_file,
    missouri_2019_file,
    "GEOID"
)

boundaries_2020 = load_boundaries(
    kansas_2020_file,
    missouri_2020_file,
    "GEOID20"
)


# Compare project tract IDs with each boundary vintage.

boundary_results = []

for vintage, boundaries in [
    ("2019", boundaries_2019),
    ("2020", boundaries_2020),
]:

    if boundaries is None:
        boundary_results.append({
            "Boundary_Vintage": vintage,
            "Boundary_File_Available": False,
            "Project_Tracts": len(project_ids),
            "Matched_Project_Tracts": None,
            "Unmatched_Project_Tracts": None,
            "Duplicate_Boundary_IDs": None,
        })
        continue

    boundary_ids = set(boundaries["GEOID"])

    matched_ids = project_ids & boundary_ids
    unmatched_ids = project_ids - boundary_ids

    duplicate_count = int(
        boundaries["GEOID"].duplicated().sum()
    )

    boundary_results.append({
        "Boundary_Vintage": vintage,
        "Boundary_File_Available": True,
        "Project_Tracts": len(project_ids),
        "Matched_Project_Tracts": len(matched_ids),
        "Unmatched_Project_Tracts": len(unmatched_ids),
        "Duplicate_Boundary_IDs": duplicate_count,
    })

    print(f"\n{vintage} BOUNDARY RESULTS")
    print("Matched project tracts:", len(matched_ids))
    print("Unmatched project tracts:", len(unmatched_ids))
    print("Duplicate boundary IDs:", duplicate_count)

    if unmatched_ids:
        print("Example unmatched IDs:", sorted(unmatched_ids)[:10])


pd.DataFrame(boundary_results).to_csv(
    boundary_report_file,
    index=False
)

print("\nBoundary ID report saved:", boundary_report_file)


# --------------------------------------------------
# Compare project polygons with matched Census polygons
# --------------------------------------------------

print("\nGEOMETRY COMPARISON")
print(
    "Comparing project geometries with Census geometries "
    "where both sources are available."
)

geometry_results = []

# EPSG:5070 is a projected CRS suitable for area comparisons
# across the contiguous United States.

for vintage, boundaries in [
    ("2019", boundaries_2019),
    ("2020", boundaries_2020),
]:

    if boundaries is None:
        continue

    if project.crs is None or boundaries.crs is None:
        print(
            f"Skipping geometry comparison for {vintage}: "
            "a CRS is missing."
        )
        continue

    project_projected = project.to_crs("EPSG:5070")
    boundary_projected = boundaries.to_crs("EPSG:5070")

    # Keep only the Census records for the project's tract IDs.

    boundary_projected = boundary_projected[
        boundary_projected["GEOID"].isin(project_ids)
    ].copy()

    # Use one record per GEOID for the comparison.
    # Stop if the boundary source contains duplicate IDs.

    if boundary_projected["GEOID"].duplicated().any():
        print(
            f"Skipping geometry comparison for {vintage}: "
            "duplicate Census boundary IDs exist."
        )
        continue

    project_lookup = project_projected.set_index("GEOID")
    boundary_lookup = boundary_projected.set_index("GEOID")

    common_ids = (
        set(project_lookup.index)
        & set(boundary_lookup.index)
    )

    for geoid in sorted(common_ids):

        project_geometry = project_lookup.loc[geoid, "geometry"]
        census_geometry = boundary_lookup.loc[geoid, "geometry"]

        if project_geometry is None or census_geometry is None:
            continue

        if project_geometry.is_empty or census_geometry.is_empty:
            continue

        # Calculate the proportion of the project polygon's area
        # that differs from the Census polygon.
        #
        # This is a diagnostic, not a legal or official boundary test.

        project_area = project_geometry.area

        if project_area == 0:
            continue

        difference_area = (
            project_geometry
            .symmetric_difference(census_geometry)
            .area
        )

        difference_percent = (
            difference_area / project_area
        ) * 100

        geometry_results.append({
            "Boundary_Vintage": vintage,
            "GEOID": geoid,
            "Project_Area_SqMeters": project_area,
            "Symmetric_Difference_SqMeters": difference_area,
            "Difference_Percent_Of_Project_Area": difference_percent,
            "Project_Geometry_Valid": project_geometry.is_valid,
            "Census_Geometry_Valid": census_geometry.is_valid,
        })


geometry_comparison = pd.DataFrame(geometry_results)

if not geometry_comparison.empty:

    geometry_comparison.to_csv(
        geometry_report_file,
        index=False
    )

    print("\nGeometry report saved:", geometry_report_file)

    print("\nGeometry comparison summary:")

    print(
        geometry_comparison.groupby("Boundary_Vintage")[
            "Difference_Percent_Of_Project_Area"
        ].agg(["count", "mean", "median", "max"]).round(6)
    )

else:
    print(
        "No geometry comparison was completed. "
        "Check the boundary paths, CRS, and ID columns."
    )


# ==================================================
# STEP 3: Inventory all USDA variables
# ==================================================

print("\n" + "=" * 60)
print("STEP 3: USDA VARIABLE INVENTORY")
print("=" * 60)


if not usda_workbook.exists():
    raise FileNotFoundError(
        f"USDA workbook not found: {usda_workbook}"
    )


# Read the official variable lookup and data sheets.

lookup = pd.read_excel(
    usda_workbook,
    sheet_name="Variable Lookup"
)

usda_data = pd.read_excel(
    usda_workbook,
    sheet_name="Food Access Research Atlas",
    nrows=5
)

print("\nUSDA data-sheet columns:", len(usda_data.columns))
print("Variable lookup rows:", len(lookup))


# Clean lookup field names and descriptions.

lookup.columns = lookup.columns.str.strip()

required_lookup_columns = [
    "Field",
    "LongName",
    "Description"
]

for column in required_lookup_columns:
    if column not in lookup.columns:
        raise ValueError(
            f"Variable Lookup sheet is missing: {column}"
        )

lookup["Field"] = lookup["Field"].astype(str).str.strip()


# All columns in the USDA data worksheet.

all_usda_fields = list(usda_data.columns)


# Seven fields currently selected in the project.

selected_fields = [
    "LA1and10",
    "LAhalfand10",
    "LILATracts_1And10",
    "lapop1share",
    "LAPOP1_10",
    "LALOWI1_10",
    "lalowi1share",
]


# Create a complete inventory of data-sheet fields.

inventory = pd.DataFrame({
    "Field": all_usda_fields
})

inventory = inventory.merge(
    lookup[
        ["Field", "LongName", "Description"]
    ].drop_duplicates("Field"),
    on="Field",
    how="left"
)

inventory["Currently_Selected_In_Project"] = (
    inventory["Field"].isin(selected_fields)
)

inventory["Definition_Available"] = (
    inventory["Description"].notna()
    & inventory["Description"].astype(str).str.strip().ne("")
)

# Add a preliminary group to help organize the review.
# This is a working classification based on field names;
# the official definition remains the source of meaning.

def classify_variable(field):

    name = field.lower()

    if field in ["CensusTract", "State", "County"]:
        return "Geography"

    if (
        "lila" in name
        or "lowincome" in name
        or "poverty" in name
        or "medianfamilyincome" in name
        or "tractlowi" in name
    ):
        return "Income and low-income access"

    if (
        "latracts" in name
        or name.startswith("la") and "share" not in name
    ):
        return "Low-access flags or counts"

    if (
        "share" in name
        or name.startswith("lapop")
        or name.startswith("lalowi")
        or name.startswith("lakids")
        or name.startswith("laseniors")
        or name.startswith("lasnap")
        or name.startswith("lahunv")
        or name.startswith("lawhite")
        or name.startswith("lablack")
        or name.startswith("laasian")
        or name.startswith("lahisp")
    ):
        return "Population counts or shares"

    if (
        "vehicle" in name
        or "hunv" in name
        or "snap" in name
    ):
        return "Vehicle or SNAP-related"

    if (
        "pop2010" in name
        or "ohu2010" in name
        or "tract" in name
        or "groupquarters" in name
        or "numgq" in name
        or "pctgq" in name
        or "urban" in name
    ):
        return "Population and tract characteristics"

    return "Other / review definition"


inventory["Preliminary_Group"] = inventory["Field"].apply(
    classify_variable
)

inventory.to_csv(
    variable_inventory_file,
    index=False
)

print("\nFull variable inventory saved:")
print(variable_inventory_file)

print("Total data-sheet fields:", len(inventory))
print(
    "Fields with a lookup definition:",
    int(inventory["Definition_Available"].sum())
)
print(
    "Fields without a lookup definition:",
    int((~inventory["Definition_Available"]).sum())
)
print(
    "Currently selected fields found:",
    int(inventory["Currently_Selected_In_Project"].sum())
)


# Create a group summary.

group_summary = (
    inventory.groupby("Preliminary_Group")
    .agg(
        Number_of_Fields=("Field", "count"),
        Fields_Selected=("Currently_Selected_In_Project", "sum"),
        Fields_With_Definitions=("Definition_Available", "sum")
    )
    .reset_index()
    .sort_values("Number_of_Fields", ascending=False)
)

group_summary.to_csv(
    variable_group_file,
    index=False
)

print("\nVariable group summary:")
print(group_summary.to_string(index=False))

print("\nGroup summary saved:")
print(variable_group_file)


# Print the selected variables and their official descriptions.

print("\nCURRENTLY SELECTED USDA CANDIDATES")

print(
    inventory.loc[
        inventory["Currently_Selected_In_Project"],
        ["Field", "LongName", "Description"]
    ].to_string(index=False)
)


print("\nSTEP 2 AND STEP 3 FINISHED.")
print("Review the generated CSV reports before making final decisions.")
