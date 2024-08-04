def receive_path_config_part(config):
    return config["path"]


def receive_source_dir_path(config):
    return receive_path_config_part(config)["source_dir"]


def receive_processed_dir_path(config):
    return receive_path_config_part(config)["processed_dir"]
