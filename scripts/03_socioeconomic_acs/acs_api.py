
import requests
import pandas as pd

url = "https://api.census.gov/data/2023/acs/acs5/variables.json"

response = requests.get(url, timeout=30)
print("Status code:", response.status_code)

if response.status_code == 200:
    variables = response.json()["variables"]

    tables_to_check = [
        "B01001", "B01003", "B03002", "B05002",
        "B08201", "B11005", "B15003", "B17001",
        "B18101", "B19013", "B19058", "B22003",
        "B25003", "B25064", "B25077"
    ]

    rows = []

    for code, info in variables.items():
        for table in tables_to_check:
            if code.startswith(table + "_") and code.endswith("E"):
                rows.append({
                    "Variable": code,
                    "Table": table,
                    "Label": info.get("label", ""),
                    "Concept": info.get("concept", "")
                })

    variable_df = pd.DataFrame(rows)
    variable_df = variable_df.drop_duplicates(
        subset=["Variable"]
    )
    variable_df = variable_df.sort_values(
        ["Table", "Variable"]
    )

    print("Variables found:", len(variable_df))
    print("\nVariables by table:")
    print(variable_df.groupby("Table").size().to_string())

    variable_df.to_csv(
        "acs_candidate_variable_definitions.csv",
        index=False
    )

    print("\nSaved: acs_candidate_variable_definitions.csv")

else:
    print(response.text)

