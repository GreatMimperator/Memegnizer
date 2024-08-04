import io
from enum import Enum
from typing import Optional
import cv2

import filetype
from PIL import Image
from numpy import ndarray


class VideoImageEnum(Enum):
    VIDEO = "video"
    IMAGE = "image"
    ANOTHER = "another"


class VideoInfo:
    def __init__(self, frame_count: int, fps: float):
        self.duration = frame_count / fps
        self.frame_count = frame_count
        self.fps = fps


def guess_video_image(path: str) -> Optional[VideoImageEnum]:
    kind = filetype.guess(path)
    if kind is None:
        return None
    if kind.mime.startswith("video") or kind.extension == "gif":
        return VideoImageEnum.VIDEO
    if kind.mime.startswith("image"):
        return VideoImageEnum.IMAGE
    return VideoImageEnum.ANOTHER


def get_video_info(video_path: str) -> VideoInfo:
    cap = cv2.VideoCapture(video_path)
    try:
        if not cap.isOpened():
            raise Exception(f"Error opening video file {video_path}")
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        return VideoInfo(frame_count, fps)
    finally:
        cap.release()


def extract_frames_from_begin_middle_end(video_path: str, video_time_padding_secs=0.5) -> list[Image]:
    cap = cv2.VideoCapture(video_path)
    try:
        if not cap.isOpened():
            raise Exception(f"Error opening video file {video_path}")

        video_info = get_video_info(video_path)

        if video_info.duration < 2 * video_time_padding_secs:
            # middle frame only
            return extract_frames(cap, [video_info.duration / 2])
        # from begin and end with padding and middle frames
        return extract_frames(
            cap,
            [
                video_time_padding_secs,
                video_info.duration / 2,
                video_info.duration - video_time_padding_secs
            ]
        )
    finally:
        cap.release()


def cv2_to_pillow_png(img: ndarray):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')

    # Seek to the start of the BytesIO buffer
    buffer.seek(0)

    # Load the PNG image back into a PIL Image object
    return Image.open(buffer)


def extract_frames(video_capture: cv2.VideoCapture, frame_timestamps_secs: list[float]) -> list[Image]:
    extracted_frames: list[Image] = []
    for frame_timestamp_secs in frame_timestamps_secs:
        video_capture.set(cv2.CAP_PROP_POS_MSEC, frame_timestamp_secs * 1000)
        is_ok_read, frame = video_capture.read()
        if not is_ok_read:
            raise Exception(f"Failed to extract frame at {frame_timestamp_secs} seconds")
        extracted_frames.append(cv2_to_pillow_png(frame))
    return extracted_frames
