
from pathlib import Path
import geopandas as gpd
import pandas as pd

project_folder = Path.home() / "Downloads" / "Urban food Production"
zip_file = Path.home() / "Downloads" / "Cadastre.gdb.zip"
output_folder = project_folder / "outputs" / "parcels"
output_folder.mkdir(parents=True, exist_ok=True)

print("Reading KCMO parcel data...")
parcels = gpd.read_file(
    f"zip://{zip_file}",
    layer="Parcels",
    engine="pyogrio"
)

# Define the official codes we want to investigate
code_labels = {
    8100: "Agricultural",
    8200: "Horticultural",
    9400: "Permanent Open Space",
    9500: "Vacant Residential",
    9600: "Vacant Non-Residential"
}

# Convert the field to numeric for reliable comparison
parcels["LANDUSECODE"] = pd.to_numeric(
    parcels["LANDUSECODE"], errors="coerce"
)

# Summarize counts for the selected codes
summary = []
for code, label in code_labels.items():
    group = parcels[parcels["LANDUSECODE"] == code]
    summary.append({
        "LANDUSECODE": code,
        "OfficialLabel": label,
        "ParcelRecords": len(group),
        "MissingParcelID": group["KIVAPIN"].isna().sum(),
        "ZeroImprovementValue": (
            pd.to_numeric(
                group["ASSESSED_IMPROVE_VALUE"], errors="coerce"
            ) == 0
        ).sum(),
        "MissingImprovementValue": (
            pd.to_numeric(
                group["ASSESSED_IMPROVE_VALUE"], errors="coerce"
            ).isna()
        ).sum(),
        "InvalidGeometry": (~group.geometry.is_valid).sum(),
        "MissingGeometry": group.geometry.isna().sum()
    })

result = pd.DataFrame(summary)
result.to_csv(
    output_folder / "candidate_landuse_summary.csv",
    index=False
)

print("\nSelected land-use code summary:")
print(result.to_string(index=False))
print("\nSaved: candidate_landuse_summary.csv")
print("These are classification-based candidates, not confirmed suitable sites.")

