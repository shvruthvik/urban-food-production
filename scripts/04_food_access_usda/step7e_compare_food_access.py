
import pandas as pd

file_path = "data/2025-sram-fara-data.xlsx"

# Read the USDA driving-distance data.
df = pd.read_excel(
    file_path,
    sheet_name="Driving Distance Data",
    header=1
)

# Identify the 14 counties in the study area.
ks_counties = [
    "Johnson", "Leavenworth", "Linn", "Miami", "Wyandotte"
]

mo_counties = [
    "Bates", "Caldwell", "Cass", "Clay", "Clinton",
    "Jackson", "Lafayette", "Platte", "Ray"
]

state = df["State"].astype(str).str.strip()

county = (
    df["County20"]
    .astype(str)
    .str.replace(" County", "", regex=False)
    .str.strip()
)

mask = (
    ((state == "Kansas") & county.isin(ks_counties))
    | ((state == "Missouri") & county.isin(mo_counties))
)

study = df.loc[mask].copy()

# Examine the two leading food-access candidates.
candidates = [
    "DD_SRAM_LA1and10",
    "DD_SRAM_lapop1share"
]

for col in candidates:
    study[col] = pd.to_numeric(study[col], errors="coerce")

print("FOOD-ACCESS INDICATOR COMPARISON")
print("================================")
print("Study-area rows:", len(study))

for col in candidates:
    values = study[col]

    print("\nIndicator:", col)
    print("Non-missing:", values.count())
    print("Missing:", values.isna().sum())
    print("Minimum:", values.min())
    print("Maximum:", values.max())
    print("Mean:", round(values.mean(), 2))
    print("Median:", round(values.median(), 2))

# Summarize the binary indicator.
print("\nLow-access flag counts:")
print(study["DD_SRAM_LA1and10"].value_counts(dropna=False))

# Save a small summary table.
summary = pd.DataFrame({
    "Indicator": candidates,
    "Non_Missing": [
        study[col].count() for col in candidates
    ],
    "Missing": [
        study[col].isna().sum() for col in candidates
    ],
    "Minimum": [
        study[col].min() for col in candidates
    ],
    "Maximum": [
        study[col].max() for col in candidates
    ],
    "Mean": [
        study[col].mean() for col in candidates
    ],
    "Median": [
        study[col].median() for col in candidates
    ]
})

summary.to_csv(
    "data/food_access_candidate_comparison.csv",
    index=False
)

print("\nSaved: data/food_access_candidate_comparison.csv")
