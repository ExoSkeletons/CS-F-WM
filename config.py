import os
import sys

import yaml
from deepmerge import always_merger
from google.cloud.firestore_v1 import Client


def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        # PyInstaller temp folder
        base_path = sys._MEIPASS
    else:
        # Running from source
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


data_dir_path = resource_path("data/")
img_dir_path = data_dir_path + "imgs/"

config = {}

max_len = {
    "wtgb": 50
}


def load_from_file():
    global config
    try:
        with open(data_dir_path + "config.yml", 'rt+') as f:
            config = always_merger.merge(config, yaml.safe_load(f))
    except OSError as e:
        print(e)
        print("Could not load config file.")


def load_from_fb(db: Client):
    global config
    try:
        snapshot = db.collection('data').document('config').get()
        if not snapshot or not snapshot.exists:
            print(f"Failed to get config document snapshot.\n{snapshot}.")
            return
        config = always_merger.merge(config, snapshot.to_dict())
    except ValueError as e:
        print(e)
        print("Could not load config from firestore.")
