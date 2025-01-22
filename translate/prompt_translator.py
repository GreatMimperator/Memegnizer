from deep_translator import GoogleTranslator
from retrying import retry

TRIES_LIMIT = 10
SLEEP_AFTER_FAIL_SECS = 10


@retry(stop_max_attempt_number=TRIES_LIMIT, wait_fixed=SLEEP_AFTER_FAIL_SECS * 1000)
def translate_from_to_ru(text: str):
    return GoogleTranslator(target='ru').translate(text)