import importlib.resources
import shutil
import os
from pathlib import Path

def extract_notebooks(destination_folder=None):
    if destination_folder is None:
        destination_folder = os.path.join(os.getcwd(), "notekit_notebooks")

    os.makedirs(destination_folder, exist_ok=True)

    try:
        notebooks_folder = importlib.resources.files("notekit").joinpath("notebooks")

        if not notebooks_folder.is_dir():
            print("The 'notekit/notebooks' folder is missing or empty.")
            return

        # Recursively copy ALL files
        for path in notebooks_folder.rglob("*"):
            if path.is_file():
                relative_path = path.relative_to(notebooks_folder)
                destination_path = Path(destination_folder) / relative_path

                destination_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(path, destination_path)

        print(f"Notebooks extracted to {destination_folder}")

    except ModuleNotFoundError:
        print("The 'notekit.notebooks' folder is missing or empty.")
