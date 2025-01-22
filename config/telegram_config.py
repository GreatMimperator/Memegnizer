def receive_telegram_config_part(config):
    return config["telegram"]

def receive_telegram_bot_token(config):
    return receive_telegram_config_part(config)["bot_token"]

def _receive_telegram_channel_id(config):
    return receive_telegram_config_part(config)["channel_id"]

def receive_linkable_telegram_channel_id(config) -> int:
    """Вернет идентификатор, который можно указывать как chat_id (добавляем -100 в начало к считанному)"""
    return int("-100" + str(_receive_telegram_channel_id(config))[1:])
