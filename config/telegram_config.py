def receive_telegram_config_part(config):
    return config["telegram"]

def receive_telegram_bot_token(config):
    return receive_telegram_config_part(config)["bot_token"]