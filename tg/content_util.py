from io import BytesIO

from PIL import Image

def get_bytearray_photo_as_image(image_as_bytearray: bytearray) -> Image:
    return Image.open(BytesIO(image_as_bytearray))