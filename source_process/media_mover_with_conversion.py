import logging
import os
import shutil
import sys

from filetype import filetype
from moviepy.editor import VideoFileClip

from PIL import Image

from config import init_config, path_config
from util import media_util, file_util, log_util
from util.log_util import init_time_count_of_logger
from util.media_util import VideoImageEnum

verbose = True
verbose_moviepy = False


def save_as_png(image_dir_path: str, image_filename: str, output_dir_path: str) -> bool:
    """:returns: True if converted before saving"""
    image_path = os.path.join(image_dir_path, image_filename)

    video_kind = filetype.guess(image_path)

    image_name_no_ext = file_util.get_file_name_without_extension(image_filename)
    output_image_name = f"{image_name_no_ext}.png"
    output_image_path = os.path.join(output_dir_path, output_image_name)

    is_in_png_already = video_kind.extension == "png"
    if is_in_png_already:
        shutil.copyfile(image_path, output_image_path)
    else:
        img = Image.open(image_path)
        img.save(output_image_path, 'PNG')
    return not is_in_png_already


def save_as_mp4_except_gif(video_dir_path: str, video_filename: str, output_dir_path: str) -> bool:
    """:returns: True if converted before saving"""
    video_path = os.path.join(video_dir_path, video_filename)

    video_kind = filetype.guess(video_path)

    video_name_no_ext = file_util.get_file_name_without_extension(video_filename)

    is_in_needed_format_already = video_kind.extension in ['gif', 'mp4']
    if is_in_needed_format_already:
        output_image_name = f"{video_name_no_ext}.{video_kind.extension}"
        output_image_path = os.path.join(output_dir_path, output_image_name)
        shutil.copyfile(video_path, output_image_path)
    else:
        video = VideoFileClip(video_path)
        output_image_name = f"{video_name_no_ext}.mp4"
        output_image_path = os.path.join(output_dir_path, output_image_name)
        moviepy_logger = "bar"
        if not verbose_moviepy:
            moviepy_logger = None
        video.write_videofile(output_image_path, codec='libx264', verbose=verbose_moviepy, logger=moviepy_logger)
    return not is_in_needed_format_already


def move_source_media_and_convert_if_needed():
    log = log_util.init_common_logger(__name__)

    image_ok_format_count = 0
    image_converted_count = 0
    video_ok_format_count = 0
    video_converted_count = 0
    another_count = 0
    none_count = 0
    already_processed_count = 0

    config = init_config.open_config()

    source_dir_path = path_config.receive_source_dir_path(config)
    if not os.path.exists(source_dir_path):
        log.error(f"Source dir {source_dir_path} does not exist")
        return

    processed_dir_path = path_config.receive_processed_dir_path(config)
    if not os.path.exists(processed_dir_path):
        log.error(f"Processed dir {processed_dir_path} does not exist")
        return
    processed_filenames_no_ext = file_util.list_dir_no_ext(processed_dir_path)

    source_dir_filenames = os.listdir(source_dir_path)
    it_log = init_time_count_of_logger(__name__)
    if not verbose:
        it_log.disabled = True
    for i, filename in enumerate(source_dir_filenames):
        file_path = os.path.join(source_dir_path, filename)
        if os.path.isdir(file_path):
            it_log.info(f"Skipped {filename} cause it is a directory", i, len(source_dir_filenames))
            continue

        filename_no_ext = file_util.get_file_name_without_extension(filename)
        if filename_no_ext in processed_filenames_no_ext:
            already_processed_count += 1
            it_log.info(f"Skipped {filename} cause it has already processed", i, len(source_dir_filenames))
            continue

        video_image_enum = media_util.guess_video_image(file_path)
        match video_image_enum:
            case VideoImageEnum.IMAGE:
                converted_before_saving = save_as_png(source_dir_path, filename, processed_dir_path)
                if converted_before_saving:
                    image_converted_count += 1
                    it_log.info(
                        f"Converted {filename} image to png before saving",
                        i, len(source_dir_filenames)
                    )
                else:
                    image_ok_format_count += 1
                    it_log.info(
                        f"Copied {filename} image (no conversion cause already in png)",
                        i, len(source_dir_filenames)
                    )

            case VideoImageEnum.VIDEO:
                converted_before_saving = save_as_mp4_except_gif(source_dir_path, filename, processed_dir_path)
                if converted_before_saving:
                    video_converted_count += 1
                    it_log.info(
                        f"Converted {filename} image to mp4 before saving",
                        i, len(source_dir_filenames)
                    )
                else:
                    video_ok_format_count += 1
                    it_log.info(
                        f"Copied {filename} video (no conversion cause already in gif or mp4)",
                        i, len(source_dir_filenames)
                    )

            case VideoImageEnum.ANOTHER:
                another_count += 1
                it_log.info(
                    f"Skipped {filename} cause it is not an image or video",
                    i, len(source_dir_filenames)
                )

            case None:
                none_count += 1
                it_log.error(
                    f"Skipped {filename} cause file type couldn't be received!",
                    i, len(source_dir_filenames)
                )

    log.info("")
    log.info(f'Already processed Count: {already_processed_count}')
    log.info(f'Image OK Format Count: {image_ok_format_count}')
    log.info(f'Image Converted Count: {image_converted_count}')
    log.info(f'Video OK Format Count: {video_ok_format_count}')
    log.info(f'Video Converted Count: {video_converted_count}')
    log.info(f'Another Count: {another_count}')
    log.info(f'None Count: {none_count}')


if __name__ == '__main__':
    move_source_media_and_convert_if_needed()
