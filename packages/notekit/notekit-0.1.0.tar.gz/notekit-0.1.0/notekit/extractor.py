import importlib.resources
import shutil
import os

def extract_notebooks(destination_folder=None):
    # Default destination folder to current working directory / notekit_notebooks
    if destination_folder is None:
        destination_folder = os.path.join(os.getcwd(), "notekit_notebooks")

    os.makedirs(destination_folder, exist_ok=True)

    # Check if the notebooks folder exists
    try:
        with importlib.resources.files("notekit.notebooks") as notebooks_folder:
            notebooks_list = list(notebooks_folder.iterdir())
            if not notebooks_list:
                print("No notebooks found in the 'notekit.notebooks' folder.")
                return  # Or raise an error if you prefer
            for nb_path in notebooks_list:
                if nb_path.suffix == ".ipynb":
                    shutil.copy(nb_path, os.path.join(destination_folder, nb_path.name))
            print(f"Notebooks extracted to {destination_folder}")
    except ModuleNotFoundError:
        print("The 'notekit.notebooks' folder is missing or empty.")
