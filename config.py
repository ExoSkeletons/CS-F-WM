import yaml

from ui.app import data_dir_path

config = {}
try:
    with open(data_dir_path + "config.yml", 'rt+') as f:
        config = yaml.safe_load(f)
except OSError as e:
    print(e)
    input("Could not load config.")
    exit(1)