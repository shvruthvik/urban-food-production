
import pandas as pd

df = pd.read_csv("acs_candidate_variable_definitions.csv")

search_terms = {
    "Age 65+": ["65 and 66 years", "67 to 69 years",
                "70 to 74 years", "75 to 79 years",
                "80 to 84 years", "85 years and over"],
    "Education": ["Bachelor's degree", "Master's degree",
                  "Professional school degree", "Doctorate degree"],
    "Disability": ["With a disability"],
    "Poverty": ["below poverty level"],
    "Vehicles": ["No vehicle available"],
    "SNAP": ["received Food Stamps/SNAP"],
    "Foreign-born": ["Foreign born"],
    "Race and ethnicity": ["Black or African American alone",
                           "Hispanic or Latino"],
    "Households with children": ["Households with one or more people under 18 years"]
}

for category, terms in search_terms.items():
    print("\n---", category, "---")

    matches = df[
        df["Label"].apply(
            lambda label: any(
                term.lower() in str(label).lower()
                for term in terms
            )
        )
    ]

    print(
        matches[["Variable", "Label"]]
        .to_string(index=False)
    )
