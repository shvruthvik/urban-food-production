
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

# Select socioeconomic indicators
columns = [
    "Poverty_Percent",
    "No_Vehicle_Households_Percent",
    "SNAP_Households_Percent"
]

# Create and save histograms
for column in columns:
    values = data[column].dropna()

    plt.figure(figsize=(8, 5))
    plt.hist(values, bins=20, edgecolor="black")

    plt.title("Distribution of " + column)
    plt.xlabel("Estimated percentage (%)")
    plt.ylabel("Number of census tracts")
    plt.tight_layout()

    file_name = column.lower() + "_distribution.png"
    plt.savefig(data_folder / file_name, dpi=150)
    plt.show()
    plt.close()

print("Socioeconomic charts saved successfully.")
