
import pandas as pd

df = pd.read_csv("acs_candidate_variable_definitions.csv")

tables = [
    "B01001", "B01003", "B03002", "B05002",
    "B08201", "B11005", "B15003", "B17001",
    "B18101", "B19013", "B19058", "B22003",
    "B25003", "B25064", "B25077"
]

for table in tables:
    print("\n---", table, "---")

    rows = df[df["Table"] == table]

    print(
        rows[["Variable", "Label"]]
        .head(8)
        .to_string(index=False)
    )

print("\nCatalog review complete.")
