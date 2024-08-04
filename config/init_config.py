import os

import yaml

from defenitions import ROOT_DIR


def open_config():
    with open(os.path.join(ROOT_DIR, "config.yaml"), 'r') as config_file:
        return yaml.safe_load(config_file)
