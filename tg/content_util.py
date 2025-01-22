from io import BytesIO

from PIL import Image
from telegram import Update
from telegram.ext import CallbackContext

from util.media_util import convert_to_jpg_bytes


async def get_message_photo_as_image(update: Update) -> Image:
    image_file = await update.message.photo[-1].get_file()
    image_bytes = await image_file.download_as_bytearray()
    return Image.open(BytesIO(image_bytes))

def get_bytearray_photo_as_image(image_as_bytearray: bytearray) -> Image:
    return Image.open(BytesIO(image_as_bytearray))

async def get_message_photo_as_jpg_bytes(update: Update) -> bytes:
    return convert_to_jpg_bytes(await get_message_photo_as_image(update))