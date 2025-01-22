from config.init_config import open_config
from tg.bot import Bot

if __name__ == '__main__':
    config = open_config()
    Bot(config).start()