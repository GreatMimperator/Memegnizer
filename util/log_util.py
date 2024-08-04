import logging
import sys
from datetime import datetime


class CustomFormatter(logging.Formatter):
    def format(self, record) -> str:
        asctime = datetime.now().strftime('%d.%m.%y %H:%M:%S')
        element_number = int(record.args[0]) + 1
        total = int(record.args[1])
        return f"{asctime} {element_number}/{total} {record.msg}"


def init_time_count_of_logger(name) -> logging.Logger:
    logger = logging.getLogger(f"tc_{name}")
    logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(CustomFormatter())

    logger.addHandler(handler)
    return logger


def init_common_logger(name) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.addHandler(logging.StreamHandler(stream=sys.stdout))

    return logger
