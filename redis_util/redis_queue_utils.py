# Пример класса для работы с Redis (очереди)
import json

import redis
from redis import Redis

from config.redis_config import receive_redis_host, receive_redis_port, receive_redis_db
from redis_util.task_model import Task


class RedisQueue:
    def __init__(self, redis_client: redis.StrictRedis, queue_name: str):
        self.redis_client = redis_client
        self.queue_name = queue_name

    def enqueue(self, task: Task):
        """Добавление задачи в очередь."""
        self.redis_client.rpush(self.queue_name, json.dumps(task.to_dict()))

    def dequeue(self) -> Task:
        """Извлечение задачи из очереди."""
        task = self.redis_client.lpop(self.queue_name)
        return Task.from_dict(json.loads(task)) if task else None


def initialize_redis(config) -> Redis:
    return redis.StrictRedis(
        host=receive_redis_host(config),
        port=int(receive_redis_port(config)),
        db=int(receive_redis_db(config))
    )