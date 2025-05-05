# Import packages
import json

# Load a JSON file into a dictionary
def json_to_dict(path: str) -> dict:
    with open(path, 'r', encoding='utf-8') as file:
        return json.load(file)