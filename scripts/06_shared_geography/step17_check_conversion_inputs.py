
import pandas as pd
from pathlib import Path

folder = Path(__file__).parent
data_folder = folder / "data"

# Input files
usda_file = data_folder / "2025-sram-fara-data.xlsx"
crosswalk_file = data_folder / "kc_metro_2010_2020_tract_relationships_complete.csv"
cdc_file = data_folder / "kc_metro_tract_data.csv"

# Read USDA population and food-access fields
usda = pd.read_excel(
    usda_file,
    sheet_name="Driving Distance Data",
    header=1,
    usecols=["CensusTract20", "DD_SRAM_LAPOP1_10"]
)

# Read population totals from the general-characteristics sheet
population = pd.read_excel(
    usda_file,
    sheet_name="GeneralTractCharacteristic Data",
    header=1,
    usecols=["CensusTract20", "POP2020"]
)

# Read the existing Census crosswalk
crosswalk = pd.read_csv(
    crosswalk_file,
    dtype={"GEOID_TRACT_10": str, "GEOID_TRACT_20": str}
)

# Check the CDC tract IDs without modifying the original file
cdc = pd.read_csv(cdc_file, dtype=str)

print("=" * 60)
print("CONVERSION INPUT CHECK")
print("=" * 60)

print("\nUSDA driving-distance rows:", len(usda))
print("USDA population rows:", len(population))
print("CDC rows:", len(cdc))
print("Crosswalk rows:", len(crosswalk))

print("\nUSDA duplicate tract IDs:")
print("Driving distance:", usda["CensusTract20"].duplicated().sum())
print("Population:", population["CensusTract20"].duplicated().sum())

print("\nMissing values:")
print("Low-access population count:", usda["DD_SRAM_LAPOP1_10"].isna().sum())
print("2020 population:", population["POP2020"].isna().sum())

# Check whether the crosswalk shares sum to one for each old tract
crosswalk["Share_of_Old_Tract_Overlap"] = pd.to_numeric(
    crosswalk["Share_of_Old_Tract_Overlap"], errors="coerce"
)

share_totals = crosswalk.groupby("GEOID_TRACT_10")[
    "Share_of_Old_Tract_Overlap"
].sum()

print("\nCrosswalk old tracts:", len(share_totals))
print(
    "Old tracts with overlap shares not approximately 1:",
    (~share_totals.between(0.99, 1.01)).sum()
)

# Check whether the USDA low-access count exceeds its population total
check = usda.merge(
    population,
    on="CensusTract20",
    how="inner",
    validate="one_to_one"
)

check["DD_SRAM_LAPOP1_10"] = pd.to_numeric(
    check["DD_SRAM_LAPOP1_10"], errors="coerce"
)
check["POP2020"] = pd.to_numeric(check["POP2020"], errors="coerce")

invalid = check[
    check["DD_SRAM_LAPOP1_10"] > check["POP2020"]
]

print("\nTracts where low-access count exceeds population:", len(invalid))

print("\nCheck complete. No files were modified.")
