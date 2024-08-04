import os
import shutil
import time
from logging import Logger
from typing import Optional

from PIL import Image
from retrying import retry
from sqlalchemy import delete, select, insert, and_
from sqlalchemy.orm import sessionmaker

from config import init_config, path_config
from db import connection, db_queries
from db.models import Prompt, File
from prompt_receive import coco_image_prompt_receiver
from util import log_util, file_util, media_util
from util.log_util import init_time_count_of_logger
from util.media_util import VideoImageEnum

force_reload = False

TRIES_LIMIT = 10
SLEEP_AFTER_FAIL_SECS = 10

log = log_util.init_common_logger(__name__)


@retry(stop_max_attempt_number=TRIES_LIMIT, wait_fixed=SLEEP_AFTER_FAIL_SECS * 1000)
def try_receive_prompt_retried(file_path: str, server_image_name: str) -> Optional[str]:
    """
    :raises Exception: of last bad try on attempts exceed
    """
    return coco_image_prompt_receiver.receive_prompt(file_path, server_image_name)


def try_receive_prompt(file_path: str, server_image_name: str) -> Optional[str]:
    """
    :raises Exception: exception with too many tries message with last try exception description addition
    """
    try:
        return try_receive_prompt_retried(file_path, server_image_name)
    except Exception as e:
        raise Exception(f"Too much exceptions, aborting... (example of last one: {e})")


if __name__ == '__main__':
    config = init_config.open_config()
    processed_dir_path = path_config.receive_processed_dir_path(config)
    engine = connection.create_postgres_engine_from_config(config)
    connection = engine.connect()
    Session = sessionmaker(connection)
    if force_reload:
        connection.execute(db_queries.delete_prompts_for_processed_dir_related_files_query(processed_dir_path))
        already_receive_prompts_filenames = []
    else:
        already_receive_prompts_filenames = (
            db_queries.select_already_received_prompts_filenames(processed_dir_path, connection=connection)
        )
    processed_dir_filenames = os.listdir(processed_dir_path)
    it_log = init_time_count_of_logger(__name__)
    for i, filename in enumerate(processed_dir_filenames):
        file_path = os.path.join(processed_dir_path, filename)
        if os.path.isdir(file_path):
            it_log.info(f"Skipping directory {filename}", i, len(processed_dir_filenames))
            continue
        filename_without_extension = file_util.get_file_name_without_extension(filename)
        if filename_without_extension in already_receive_prompts_filenames:
            it_log.info(
                f"Skipping {filename} because it already received before (set force_reload to True to update all)",
                i, len(processed_dir_filenames)
            )
            continue
        prompts: list[str] = []
        video_image_enum = media_util.guess_video_image(file_path)
        match video_image_enum:
            case VideoImageEnum.IMAGE:
                prompts.append(try_receive_prompt(file_path, filename))

            case VideoImageEnum.VIDEO:
                try:
                    frames = media_util.extract_frames_from_begin_middle_end(file_path)
                except Exception as e:
                    it_log.info(
                        f"Skipping {filename} because could not extract frames with exception: {e}",
                        i, len(processed_dir_filenames)
                    )
                    continue
                for j, frame in enumerate(frames):
                    server_image_name = f"{j}-{filename_without_extension}.png"
                    temp_filename = f"frame-{j}.png"
                    temp_filepath = os.path.join(path_config.receive_tmp_dir_path(config), temp_filename)
                    try:
                        frame.save(temp_filepath, format="PNG")
                        prompt = try_receive_prompt(temp_filepath, server_image_name)
                    finally:
                        os.remove(temp_filepath)
                        frame.close()
                    prompts.append(prompt)

            case VideoImageEnum.ANOTHER:
                it_log.info(
                    f"Skipping {filename} because its media type is not video or image!",
                    i, len(processed_dir_filenames)
                )
                continue

            case None:
                it_log.info(
                    f"Skipping {filename} because its media type cannot be received!",
                    i, len(processed_dir_filenames)
                )
                continue

        file_id = db_queries.select_file_id(processed_dir_path, filename_without_extension, connection=connection)
        with Session() as session:
            if file_id is None:
                file_id = db_queries.insert_file_get_id(processed_dir_path, filename_without_extension, session=session)
                it_log.info(
                    f"Added {filename} to files - not captured before!",
                    i, len(processed_dir_filenames)
                )
            else:
                it_log.info(
                    f"Selected {filename} id from files - captured before",
                    i, len(processed_dir_filenames)
                )
            session.execute(insert(Prompt).values(file_id=file_id, text="\n\n".join(prompts)))
            it_log.info(
                f"{filename} prompt receive and save complete!",
                i, len(processed_dir_filenames)
            )
            session.commit()
            connection.commit()
