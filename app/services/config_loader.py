import json


def load_static_config():
    with open("app/data/static_config.json", "r", encoding="utf-8") as file:
        parsed_file = json.load(file)
    return parsed_file


