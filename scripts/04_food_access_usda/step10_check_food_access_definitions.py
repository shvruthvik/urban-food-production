
import pandas as pd

file_path = "data/2025-sram-fara-data.xlsx"

lookup = pd.read_excel(
    file_path,
    sheet_name="VL_Driving Distance",
    header=None
)

# Search the lookup sheet for relevant indicator definitions.
terms = [
    "DD_SRAM_LA1and10",
    "DD_SRAM_LILATracts_1And10",
    "DD_SRAM_lapop1share",
    "DD_SRAM_lapop1",
    "DD_SRAM_LAPOP1_10"
]

print("FOOD-ACCESS INDICATOR DEFINITIONS")
print("=" * 45)

for term in terms:
    matches = lookup.astype(str).apply(
        lambda column: column.str.contains(
            term, case=False, na=False
        )
    ).any(axis=1)

    print(f"\nSearch: {term}")

    if matches.any():
        print(lookup.loc[matches].to_string(index=False, header=False))
    else:
        print("No match found in this sheet.")

print("\nCheck complete.")
