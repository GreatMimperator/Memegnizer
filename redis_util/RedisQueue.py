# Пример класса для работы с Redis (очереди)
import json

import redis
from redis import Redis

from config.redis_config import receive_redis_config


class RedisQueue:
    def __init__(self, redis_client: redis.StrictRedis, queue_name: str):
        self.redis_client = redis_client
        self.queue_name = queue_name

    def enqueue(self, task: dict):
        """Добавление задачи в очередь."""
        self.redis_client.rpush(self.queue_name, json.dumps(task))

    def dequeue(self):
        """Извлечение задачи из очереди."""
        task = self.redis_client.lpop(self.queue_name)
        return json.loads(task) if task else None


# Инициализация Redis
def initialize_redis(config) -> Redis:
    redis_config = receive_redis_config(config)
    redis_client = redis.StrictRedis(
        host=redis_config["host"], 
        port=int(redis_config["port"]),
        db=int(redis_config["db"])
    )
    return redis_client