
from pathlib import Path
import geopandas as gpd
import pandas as pd

project_folder = Path.home() / "Downloads" / "Urban food Production"

tract_file = project_folder / "data" / "kc_metro_tracts_with_data.geojson"
parcel_file = (
    project_folder / "outputs" / "parcels"
    / "kcmo_candidates_in_study_area.geojson"
)
output_folder = project_folder / "outputs" / "parcels"
output_folder.mkdir(parents=True, exist_ok=True)

print("Reading tracts and candidate parcels...")

tracts = gpd.read_file(tract_file)
parcels = gpd.read_file(parcel_file)

# Use a common projected CRS for spatial operations
analysis_crs = "EPSG:26915"
tracts = tracts.to_crs(analysis_crs)
parcels = parcels.to_crs(analysis_crs)

# Remove missing or empty geometries
tracts = tracts[
    tracts.geometry.notna() & ~tracts.geometry.is_empty
].copy()

parcels = parcels[
    parcels.geometry.notna() & ~parcels.geometry.is_empty
].copy()

# Repair invalid geometries before spatial operations
tracts["geometry"] = tracts.geometry.make_valid()
parcels["geometry"] = parcels.geometry.make_valid()

# Confirm the tract ID field exists
if "GEOID" not in tracts.columns:
    raise ValueError(
        "GEOID field not found. Check the tract file's column names."
    )

# Use a point guaranteed to lie within each parcel polygon
parcels["assignment_point"] = parcels.geometry.representative_point()

parcel_points = gpd.GeoDataFrame(
    parcels.drop(columns="geometry"),
    geometry="assignment_point",
    crs=parcels.crs
)

# Assign each representative point to its containing census tract
joined = gpd.sjoin(
    parcel_points,
    tracts[["GEOID", "geometry"]],
    how="left",
    predicate="within"
)

# Report the assignment quality
total_parcels = len(joined)
assigned = joined["GEOID"].notna().sum()
unassigned = joined["GEOID"].isna().sum()
duplicate_assignments = joined.duplicated(
    subset=["KIVAPIN"], keep=False
).sum() if "KIVAPIN" in joined.columns else 0

print("\nSPATIAL ASSIGNMENT RESULTS")
print("Parcel records processed:", total_parcels)
print("Assigned to a tract:", assigned)
print("Not assigned to a tract:", unassigned)
print("Rows with repeated KIVAPIN values:", duplicate_assignments)

# Save parcel-to-tract assignments, retaining parcel attributes
assignment_columns = [
    column for column in [
        "KIVAPIN", "APN", "ADDRESS", "LANDUSECODE",
        "ASSESSED_LAND_VALUE", "ASSESSED_IMPROVE_VALUE",
        "Area_SqFt", "GEOID"
    ] if column in joined.columns
]

assignments = joined[assignment_columns].copy()
assignments.to_csv(
    output_folder / "candidate_parcel_tract_assignments.csv",
    index=False
)

# Summarize candidate parcels by tract
assigned_rows = joined[joined["GEOID"].notna()].copy()

tract_summary = (
    assigned_rows.groupby(["GEOID", "LANDUSECODE"])
    .size()
    .unstack(fill_value=0)
    .reset_index()
)

tract_summary.columns = [
    "GEOID" if column == "GEOID"
    else f"Code_{int(column)}_Count"
    for column in tract_summary.columns
]

tract_summary["TotalCandidateParcels"] = (
    tract_summary.drop(columns="GEOID").sum(axis=1)
)

tract_summary.to_csv(
    output_folder / "candidate_parcel_counts_by_tract.csv",
    index=False
)

# Save the number of parcels not assigned to any tract for review
joined.loc[joined["GEOID"].isna(), assignment_columns].to_csv(
    output_folder / "unassigned_candidate_parcels.csv",
    index=False
)

print("\nSaved outputs:")
print("candidate_parcel_tract_assignments.csv")
print("candidate_parcel_counts_by_tract.csv")
print("unassigned_candidate_parcels.csv")
print("\nAssignment uses a representative point, not the largest-overlap rule.")
print("Counts describe classified candidate parcels, not confirmed suitable sites.")
