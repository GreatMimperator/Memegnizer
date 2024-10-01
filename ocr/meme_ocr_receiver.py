import os
import time

from sqlalchemy import insert
from sqlalchemy.orm import sessionmaker

from config import init_config, path_config
from db import db_queries
from db.connection import create_postgres_engine_from_config
from db.models import Ocr
from lib.ocr_selenium_receiver import receive_image_ocr
from util import media_util, file_util
from util.log_util import init_time_count_of_logger
from util.media_util import VideoImageEnum

verbose = True


def ocr_receive():
    config = init_config.open_config()
    processed_dir_path = path_config.receive_processed_dir_path(config)

    engine = create_postgres_engine_from_config(config)
    connection = engine.connect()
    Session = sessionmaker(connection)

    ocr_done_filenames = db_queries.select_ocr_done_filenames_for_processed_dir(processed_dir_path, Session)

    input_dir_file_names = os.listdir(processed_dir_path)
    input_dir_file_count = len(input_dir_file_names)
    input_dir_db_registered_image_files_id_and_name = []
    it_log = init_time_count_of_logger(__name__)
    if not verbose:
        it_log.disabled = True
    for i, file_name in enumerate(input_dir_file_names):
        file_path = os.path.join(processed_dir_path, file_name)
        if os.path.isdir(file_path):
            it_log.info(
                f"Skipping {file_name} because it is a directory",
                i, input_dir_file_count
            )
            continue
        # TODO: добавить обработку видео - брать кадр из середины видео
        if media_util.guess_video_image(file_path) != VideoImageEnum.IMAGE:
            it_log.info(
                f"Skipping {file_name} because it is not an image file",
                i, input_dir_file_count
            )
            continue
        file_name_no_ext = file_util.get_file_name_without_extension(file_name)
        if file_name_no_ext in ocr_done_filenames:
            it_log.info(
                f"Skipping {file_name} because it has already processed",
                i, input_dir_file_count
            )
            continue
        file_id = db_queries.select_file_id(processed_dir_path, file_name_no_ext, connection=connection)
        if file_id is None:
            it_log.info(
                f"Skipping {file_name} because file does not exists in db",
                i, input_dir_file_count
            )
            continue
        input_dir_db_registered_image_files_id_and_name.append((file_id, file_name))
        it_log.info(
            f"Added {file_name} image to process list",
            i, input_dir_file_count
        )
    input_dir_db_registered_image_file_count = len(input_dir_db_registered_image_files_id_and_name)
    for i, (file_id, file_name) in enumerate(input_dir_db_registered_image_files_id_and_name):
        file_path = os.path.join(processed_dir_path, file_name)
        ocr_text = receive_image_ocr(file_path)
        db_queries.execute_insert_in_session(
            insert(Ocr).values(ocr=ocr_text, file_id=file_id),
            Session,
            connection
        )
        it_log.info(
            f"Requested and put to db {file_name} image ocr successfully!",
            i, input_dir_db_registered_image_file_count
        )


if __name__ == '__main__':
    while True:
        time.sleep(1800)
        ocr_receive()
