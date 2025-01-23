# Получаем конфигурацию для Redis
def receive_redis_config_part(config):
    return config["redis"]

# Получаем параметры подключения к Redis
def receive_redis_config(config):
    redis_config = receive_redis_config_part(config)
    return {
        "host": redis_config["host"],
        "port": redis_config["port"],
        "db": redis_config["db"]
    }