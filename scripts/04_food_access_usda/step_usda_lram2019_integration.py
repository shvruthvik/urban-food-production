
"""
USDA 2019 Large Retailer Access Map (LRAM) Integration

Purpose:
1. Load the original USDA workbook.
2. Verify census tract IDs.
3. Filter USDA data to our 516 project tracts.
4. Merge selected USDA indicators with our existing dataset.
5. Validate the merged output.
6. Save the results and quality reports.

Required packages:
pip install pandas openpyxl
"""

import pandas as pd
from pathlib import Path

# --------------------------------------------------
# STEP 1: Set file paths
# --------------------------------------------------

data_folder = Path("data")

usda_file = data_folder / "FoodAccessResearchAtlasData2019.xlsx"

project_file = (
    data_folder / "kc_metro_combined_health_socioeconomic.csv"
)

filtered_file = data_folder / "LRAM_2019_project_tracts_516.csv"

merged_file = (
    data_folder / "kc_metro_combined_health_socioeconomic_LRAM2019.csv"
)

quality_file = data_folder / "LRAM2019_merge_quality_check.csv"

summary_file = data_folder / "LRAM2019_merged_variable_summary.csv"

notes_file = data_folder / "LRAM2019_analysis_notes.txt"


# --------------------------------------------------
# STEP 2: Check that the input files exist
# --------------------------------------------------

if not usda_file.exists():
    raise FileNotFoundError(
        f"USDA workbook not found: {usda_file}"
    )

if not project_file.exists():
    raise FileNotFoundError(
        f"Project dataset not found: {project_file}"
    )

print("Both input files were found.")


# --------------------------------------------------
# STEP 3: Load the existing project dataset
# --------------------------------------------------

project = pd.read_csv(
    project_file,
    dtype={"TractFIPS": str}
)

# Census tract IDs must be treated as text, not numbers.
# This helps preserve leading zeros.

project["TractFIPS"] = (
    project["TractFIPS"]
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

print("\nPROJECT DATASET")
print("Rows:", len(project))
print("Unique tracts:", project["TractFIPS"].nunique())


# Check for missing or duplicate project tract IDs.

if project["TractFIPS"].isna().any():
    raise ValueError("Project dataset has missing tract IDs.")

if project["TractFIPS"].duplicated().any():
    raise ValueError("Project dataset has duplicate tract IDs.")


# --------------------------------------------------
# STEP 4: Load the original USDA workbook
# --------------------------------------------------

usda = pd.read_excel(
    usda_file,
    sheet_name="Food Access Research Atlas",
    dtype={"CensusTract": str}
)

usda["CensusTract"] = (
    usda["CensusTract"]
    .str.strip()
    .str.replace(r"\.0$", "", regex=True)
    .str.zfill(11)
)

print("\nORIGINAL USDA DATASET")
print("Rows:", len(usda))
print("Unique tract IDs:", usda["CensusTract"].nunique())


# Check the USDA tract IDs.

if usda["CensusTract"].isna().any():
    raise ValueError("USDA dataset has missing tract IDs.")

if usda["CensusTract"].duplicated().any():
    raise ValueError("USDA dataset has duplicate tract IDs.")


# --------------------------------------------------
# STEP 5: Select the USDA candidate indicators
# --------------------------------------------------

candidate_columns = [
    "LA1and10",
    "LAhalfand10",
    "LILATracts_1And10",
    "lapop1share",
    "LAPOP1_10",
    "LALOWI1_10",
    "lalowi1share"
]

# Check that all expected columns exist.

for column in candidate_columns:
    if column not in usda.columns:
        raise ValueError(
            f"Column not found in USDA workbook: {column}"
        )


# --------------------------------------------------
# STEP 6: Filter USDA records to our project area
# --------------------------------------------------

project_tracts = set(project["TractFIPS"])

usda_project = usda[
    usda["CensusTract"].isin(project_tracts)
].copy()

usda_tracts = set(usda_project["CensusTract"])

missing_tracts = project_tracts - usda_tracts

extra_tracts = usda_tracts - project_tracts

print("\nGEOGRAPHIC MATCH CHECK")
print("Project tracts:", len(project_tracts))
print("USDA tracts retained:", len(usda_project))
print("Project tracts missing from USDA:", len(missing_tracts))
print("Unexpected extra tracts:", len(extra_tracts))

# Stop if some project tracts cannot be matched.

if missing_tracts:
    print("Example unmatched IDs:", list(missing_tracts)[:10])
    raise ValueError("Some project tracts did not match USDA.")

if extra_tracts:
    raise ValueError("Unexpected USDA tracts remain after filtering.")


# Save the filtered USDA records for traceability.

usda_project.to_csv(filtered_file, index=False)

print("Filtered USDA dataset saved.")


# --------------------------------------------------
# STEP 7: Keep and rename selected USDA columns
# --------------------------------------------------

usda_selected = usda_project[
    ["CensusTract"] + candidate_columns
].copy()

# Rename the USDA tract ID to match the project dataset.
# Add a prefix to distinguish USDA variables from ACS/PLACES.

usda_selected = usda_selected.rename(
    columns={
        "CensusTract": "TractFIPS",
        **{
            column: "LRAM2019_" + column
            for column in candidate_columns
        }
    }
)

# Convert indicator values to numeric.
# Invalid or blank values become missing, not zero.

for column in usda_selected.columns:
    if column != "TractFIPS":
        usda_selected[column] = pd.to_numeric(
            usda_selected[column],
            errors="coerce"
        )


# --------------------------------------------------
# STEP 8: Merge USDA with the project dataset
# --------------------------------------------------

merged = project.merge(
    usda_selected,
    on="TractFIPS",
    how="left",
    validate="one_to_one",
    indicator=True
)

matched_count = (merged["_merge"] == "both").sum()

unmatched_count = (merged["_merge"] == "left_only").sum()

# Remove the temporary merge-status column.

merged = merged.drop(columns=["_merge"])


# --------------------------------------------------
# STEP 9: Validate the merged dataset
# --------------------------------------------------

print("\nMERGE VALIDATION")
print("Original project rows:", len(project))
print("Merged rows:", len(merged))
print("Unique tracts after merge:", merged["TractFIPS"].nunique())
print("Matched tracts:", matched_count)
print("Unmatched project tracts:", unmatched_count)
print(
    "Duplicate tract IDs after merge:",
    merged["TractFIPS"].duplicated().sum()
)

# Confirm that no project rows were lost or duplicated.

if len(merged) != len(project):
    raise ValueError("The number of rows changed after merging.")

if merged["TractFIPS"].nunique() != project["TractFIPS"].nunique():
    raise ValueError("The unique tract count changed after merging.")

if merged["TractFIPS"].duplicated().any():
    raise ValueError("Duplicate tract IDs were created.")

if unmatched_count != 0:
    raise ValueError("Some project tracts failed to match USDA.")


# --------------------------------------------------
# STEP 10: Save the merged dataset
# --------------------------------------------------

merged.to_csv(merged_file, index=False)

print("\nMerged dataset saved to:")
print(merged_file)


# --------------------------------------------------
# STEP 11: Summarize the USDA indicators
# --------------------------------------------------

summary_rows = []

for column in candidate_columns:

    full_column_name = "LRAM2019_" + column

    values = merged[full_column_name]

    summary_rows.append({
        "Column": full_column_name,
        "Non_missing": values.notna().sum(),
        "Missing": values.isna().sum(),
        "Unique_values": values.nunique(),
        "Minimum": values.min(),
        "Maximum": values.max(),
        "Mean": values.mean(),
        "Median": values.median()
    })

summary = pd.DataFrame(summary_rows)

summary.to_csv(summary_file, index=False)

print("\nUSDA INDICATOR SUMMARY")
print(summary.to_string(index=False))


# --------------------------------------------------
# STEP 12: Save the merge quality report
# --------------------------------------------------

quality_report = pd.DataFrame([{
    "Project_rows_before_merge": len(project),
    "Project_unique_tracts": project["TractFIPS"].nunique(),
    "Original_USDA_rows": len(usda),
    "Original_USDA_unique_tracts": usda["CensusTract"].nunique(),
    "USDA_project_rows": len(usda_project),
    "Matched_tracts": matched_count,
    "Unmatched_tracts": unmatched_count,
    "Merged_rows": len(merged),
    "Merged_unique_tracts": merged["TractFIPS"].nunique(),
    "Duplicate_tract_IDs": merged["TractFIPS"].duplicated().sum(),
    "USDA_columns_added": len(candidate_columns)
}])

quality_report.to_csv(quality_file, index=False)

print("\nQuality report saved to:")
print(quality_file)


# --------------------------------------------------
# STEP 13: Save methodology notes
# --------------------------------------------------

notes = """
USDA 2019 Large Retailer Access Map (LRAM)

Source:
FoodAccessResearchAtlasData2019.xlsx
Worksheet: Food Access Research Atlas

Merge key:
Project dataset: TractFIPS
USDA dataset: CensusTract

The IDs were standardized as 11-character text values.
The USDA records were filtered to the project's tract IDs.
The selected fields were merged using a one-to-one left join.

Candidate indicators:
- LA1and10
- LAhalfand10
- LILATracts_1And10
- lapop1share
- LAPOP1_10
- LALOWI1_10
- lalowi1share

Important interpretation:
LRAM measures geographic access to large food retailers,
such as supermarkets, supercenters, and large grocery stores.
It is not a direct measure of individual food insecurity.
It is not the same measure as SNAP-authorized retailer access.

The 2019 LRAM is documented by USDA as using 2010 census
tract geography. Matching IDs establishes tabular join
compatibility, but does not by itself prove that the project's
actual boundary polygons are identical.

Missing values were kept as missing, not changed to zero.

The indicators remain candidates until the final model
criteria are reviewed for overlap and double-counting.
"""

notes_file.write_text(notes, encoding="utf-8")

print("\nMethodology notes saved to:")
print(notes_file)

print("\nUSDA integration and validation completed successfully.")
