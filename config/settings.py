
import json
import os


SETTINGS_FILE = os.path.join(
    os.path.dirname(__file__),
    "settings.json"
)


def get_settings():

    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)
