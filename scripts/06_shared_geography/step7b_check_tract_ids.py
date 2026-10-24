
import pandas as pd
from pathlib import Path

data_path = Path("data") / "kc_metro_combined_health_socioeconomic.csv"

# Read identifiers as text to preserve leading zeros
data = pd.read_csv(data_path, dtype=str)

print("Sample tract identifiers:")
print(data[["StateAbbr", "CountyFIPS", "TractFIPS"]].head(15).to_string(index=False))

print("\nTractFIPS lengths:")
print(data["TractFIPS"].str.strip().str.len().value_counts(dropna=False))

print("\nCountyFIPS lengths:")
print(data["CountyFIPS"].str.strip().str.len().value_counts(dropna=False))

print("\nStates in dataset:")
print(data["StateAbbr"].value_counts(dropna=False))

print("\nMissing tract IDs:", data["TractFIPS"].isna().sum())
print("Duplicate tract IDs:", data["TractFIPS"].duplicated().sum())
