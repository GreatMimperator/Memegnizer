import io
import os
import tempfile
from typing import Optional

from moviepy import VideoFileClip

import cv2
import numpy as np
from PIL import Image


class VideoInfo:
    def __init__(self, frame_count: int, fps: float):
        self.duration = frame_count / fps
        self.frame_count = frame_count
        self.fps = fps


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

def cv2_to_pillow_png(img: np.ndarray):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
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

def convert_to_jpg_bytes(image: Image):
    image_rgb = image.convert('RGB')
    img_byte_arr = io.BytesIO()
    image_rgb.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()

def extract_frames_from_begin_middle_end_video_bytearray(video_data: bytearray, video_time_padding_secs=0.5):
    # Создаём уникальный временный файл для передачи в extract_frames_from_begin_middle_end
    with tempfile.NamedTemporaryFile(delete=False) as temp_video_file:
        temp_video_file.write(video_data)
        temp_video_path = temp_video_file.name

    try:
        # Теперь вызываем функцию с созданным временным файлом
        return extract_frames_from_begin_middle_end(temp_video_path, video_time_padding_secs)
    finally:
        # Удаляем временный файл после использования
        if os.path.exists(temp_video_path):
            os.remove(temp_video_path)

def extract_audio_from_mp4(mp4_bytearray) -> Optional[str]:
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as temp_video_file:
        temp_video_file.write(mp4_bytearray)
        temp_video_file_path = temp_video_file.name

    video_clip = VideoFileClip(temp_video_file_path)
    audio_clip = video_clip.audio

    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_audio_file:
        audio_path = temp_audio_file.name
        try:
            audio_clip.write_audiofile(audio_path)  # Save audio as WAV file
        except Exception as e:
            # gif, no sound
            return None

    os.remove(temp_video_file_path)

    return audio_path