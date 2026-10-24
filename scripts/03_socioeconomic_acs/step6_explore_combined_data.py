
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load the combined dataset
project_folder = Path(__file__).resolve().parents[2]
data_folder = project_folder / "data" / "processed" / "integrated"

data = pd.read_csv(
    data_folder / "kc_metro_combined_health_socioeconomic.csv",
    dtype={"TractFIPS": str}
)

# Select the three health indicators
health_columns = [
    "OBESITY_CrudePrev",
    "DIABETES_CrudePrev",
    "BPHIGH_CrudePrev"
]

# Create one histogram for each health indicator
for column in health_columns:
    data[column].dropna().hist(bins=20, edgecolor="black")
    plt.title("Distribution of " + column)
    plt.xlabel("Estimated prevalence (%)")
    plt.ylabel("Number of census tracts")
    plt.tight_layout()

    # Save the chart
    chart_name = column.lower() + "_distribution.png"
    plt.savefig(data_folder / chart_name, dpi=150)
    plt.show()
    plt.close()

print("Health indicator charts saved in the data folder.")

