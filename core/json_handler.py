import json


def write_json(path_to_json, new_data):
    with open(path_to_json, 'r+') as file:
        file_data = json.load(file)
        file_data["users"].append(new_data)
        file.seek(0)
        json.dump(file_data, file, indent=4)
