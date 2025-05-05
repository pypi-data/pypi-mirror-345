# filetools.py
# Import packages
import json, shutil, os

# Load a JSON file into a dictionary
def json_to_dict(path: str) -> dict:
    """
    Load a JSON file from the specified path and return its contents as a dictionary.

    :param path: The file path to the JSON file to be loaded.
    :return: A dictionary representation of the JSON file's contents.
    :raises Exception: If there is an error loading the JSON file.
    """

    try:
        with open(path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except Exception as e:
        raise Exception(f"Error loading JSON file: {e}")

def dict_to_json(path: str, data: dict) -> None:
    """
    Save a dictionary to the specified path as a JSON file.

    :param path: The file path to save the JSON file to.
    :param data: The dictionary to be saved as a JSON file.
    :raises Exception: If there is an error saving the JSON file.
    """
    
    try:
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        raise Exception(f"Error saving JSON file: {e}")

def copy_file(src: str, dst: str, overwrite: bool = False) -> None:
    """
    Copy a file from source to destination.
    :param src: Source file path.
    :param dst: Destination file path.
    :param overwrite: If True, overwrite existing destination file.
    :raises Exception: If copying fails or destination exists and overwrite is False.
    """
    try:
        if os.path.exists(dst) and not overwrite:
            raise Exception("Destination file exists and overwrite is False")
        shutil.copy2(src, dst)
    except Exception as e:
        raise Exception(f"Error copying file: {e}")