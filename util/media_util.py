from enum import Enum
from typing import Optional

import filetype


class VideoImageEnum(Enum):
    VIDEO = "video"
    IMAGE = "image"
    ANOTHER = "another"


def guess_video_image(path: str) -> Optional[VideoImageEnum]:
    kind = filetype.guess(path)
    if kind is None:
        return None
    if kind.mime.startswith("video") or kind.extension == "gif":
        return VideoImageEnum.VIDEO
    if kind.mime.startswith("image"):
        return VideoImageEnum.IMAGE
    return VideoImageEnum.ANOTHER
