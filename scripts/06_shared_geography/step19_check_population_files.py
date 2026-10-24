
from pathlib import Path

folder = Path(__file__).parent
data_folder = folder / "data"

print("Checking existing data files...\n")

for file in sorted(data_folder.rglob("*")):
    if file.is_file():
        name = file.name.lower()

        if any(word in name for word in [
            "population",
            "block",
            "crosswalk",
            "relationship",
            "census",
            "tract"
        ]):
            print(file.relative_to(folder))

print("\nFile check complete. No files were modified.")
