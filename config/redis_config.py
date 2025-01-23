# Получаем конфигурацию для Redis
def receive_redis_config_part(config):
    return config["redis"]

def receive_redis_host(config):
    return receive_redis_config_part(config)["host"]

def receive_redis_port(config):
    return receive_redis_config_part(config)["port"]

def receive_redis_db(config):
    return receive_redis_config_part(config)["db"]
