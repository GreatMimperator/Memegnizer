import itertools
import os.path
import time

from deep_translator import GoogleTranslator
from retrying import retry
from sqlalchemy import select, update, insert
from sqlalchemy.orm import sessionmaker

from config import init_config, path_config
from db import db_queries, connection
from db.connection import create_postgres_engine_from_config
from db.models import TranslatedPrompt, Prompt, File
from util.log_util import init_time_count_of_logger

force_reload = False
verbose = True

TRIES_LIMIT = 10
SLEEP_AFTER_FAIL_SECS = 10


@retry(stop_max_attempt_number=TRIES_LIMIT, wait_fixed=SLEEP_AFTER_FAIL_SECS * 1000)
def translate_from_en_to_ru(text: str):
    return GoogleTranslator(source='en', target='ru').translate(text)


def prompts_translation_receive():
    config = init_config.open_config()
    processed_dir_path = path_config.receive_processed_dir_path(config)

    engine = create_postgres_engine_from_config(config)
    connection = engine.connect()
    Session = sessionmaker(connection)

    if force_reload:
        db_queries.delete_translated_prompts_for_processed_dir_related_files(processed_dir_path, connection=connection)
        existing_translated_prompts_filenames_no_ext = []
    else:
        existing_translated_prompts_filenames_no_ext = (
            db_queries.select_translated_prompts_filenames_for_processed_dir(processed_dir_path, session_maker=Session)
        )
    file_and_prompt_sequence = (
        db_queries.select_file_and_prompt_for_processed_dir(processed_dir_path, session_maker=Session)
    )
    prompts_count = len(file_and_prompt_sequence)
    it_log = init_time_count_of_logger(__name__)
    if not verbose:
        it_log.disabled = True
    for i, (file, prompt) in enumerate(file_and_prompt_sequence):
        if file.filename_without_extension in existing_translated_prompts_filenames_no_ext:
            it_log.info(
                f"Skipping {file.filename_without_extension} because its translation already exists",
                i, prompts_count
            )
            continue
        translated_text = translate_from_en_to_ru(prompt.text)
        db_queries.execute_insert_in_session(
            insert(TranslatedPrompt).values(file_id=file.id, text=translated_text),
            Session, connection
        )
        it_log.info(
            f"Translated and saved prompt of {file.filename_without_extension} successfully!",
            i, prompts_count
        )


if __name__ == '__main__':
    while True:
        time.sleep(1800)
        prompts_translation_receive()
