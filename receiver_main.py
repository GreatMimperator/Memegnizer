from config.init_config import open_config
from redis_util.redis_queue_utils import RedisQueue, initialize_redis
from tg.receiver_bot import MessageReceiver

if __name__ == '__main__':
    config = open_config()
    redis_queue = RedisQueue(initialize_redis(config), "tasks")
    MessageReceiver(config, redis_queue).start()