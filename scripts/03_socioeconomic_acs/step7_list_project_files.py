
from pathlib import Path

project_folder = Path.cwd()

for file in sorted(project_folder.rglob("*")):
    if file.is_file():
        print(file.relative_to(project_folder))
