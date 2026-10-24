
import pandas as pd

df = pd.read_csv("acs_candidate_variable_definitions.csv")

checks = {
    "B05002": ["Foreign", "Total:"],
    "B08201": ["Total:", "No vehicle available"],
    "B15003": ["Total:", "Bachelor's degree",
               "Master's degree", "Professional school degree",
               "Doctorate degree"],
    "B18101": ["Total:", "With a disability"],
    "B22003": ["Total:", "received Food Stamps/SNAP"],
    "B17001": ["Total:", "below poverty level"]
}

for table, terms in checks.items():
    print("\n---", table, "---")

    rows = df[df["Table"] == table]

    for term in terms:
        found = rows[
            rows["Label"].str.contains(
                term, case=False, na=False
            )
        ]

        print("\nSearch:", term)
        print(
            found[["Variable", "Label"]]
            .head(10)
            .to_string(index=False)
        )

