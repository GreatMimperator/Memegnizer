import os
from defenitions import ROOT_DIR

import yaml


def open_config():
    with open(os.path.join(ROOT_DIR, "config.yaml"), 'r') as config_file:
        return yaml.safe_load(config_file)


def receive_postgres_config_part(config):
    return config["postgres"]


def receive_postgres_database(config):
    return receive_postgres_config_part(config)["database"]


def receive_postgres_user(config):
    return receive_postgres_config_part(config)["user"]


def receive_postgres_password(config):
    return receive_postgres_config_part(config)["password"]


def receive_postgres_host(config):
    return receive_postgres_config_part(config)["host"]


def receive_postgres_port(config):
    return receive_postgres_config_part(config)["port"]
