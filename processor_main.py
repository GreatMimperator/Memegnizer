import asyncio

from config.init_config import open_config
from redis_util.RedisQueue import initialize_redis, RedisQueue
from tg.processor_bot import TaskController

if __name__ == '__main__':
    config = open_config()
    redis_queue = RedisQueue(initialize_redis(config), "tasks")
    asyncio.run(TaskController(config, redis_queue).start())
