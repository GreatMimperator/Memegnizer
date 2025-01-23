import easyocr
from PIL import Image
from telegram import Update, File
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters

from config.telegram_config import receive_telegram_bot_token, receive_linkable_telegram_channel_id
from ocr.meme_ocr_receiver import ocr_image
from tg.content_util import get_bytearray_photo_as_image
from tools.llm import ollama_kit
from translate.prompt_translator import translate_from_to_ru
from util.media_util import convert_to_jpg_bytes, extract_frames_from_begin_middle_end_video_bytearray


class TaskProcessor:

    def __init__(self, config):
        self.config = config
        self.ocr_reader = easyocr.Reader(['ru', 'en'], gpu=False) # loads in memory once

    async def _picture_message_process(self, pil_image: Image, context: CallbackContext):
        jpg_image_bytes = convert_to_jpg_bytes(pil_image)
        image_description = ollama_kit.ollama_image_describe(jpg_image_bytes, self.config)
        translated_image_description = translate_from_to_ru(image_description)
        await context.bot.send_message(
            chat_id=receive_linkable_telegram_channel_id(self.config),
            text=translated_image_description
        )
        ocr_text = ocr_image(pil_image, self.ocr_reader)
        if len(ocr_text) > 1: # может возвращать один символ, например кавычку - нам это не нужно
            await context.bot.send_message(chat_id=receive_linkable_telegram_channel_id(self.config), text=ocr_text)
            ocr_text_translated = translate_from_to_ru(ocr_text)
            if ocr_text_translated is not None and len(ocr_text_translated) > 1:
                await context.bot.send_message(
                    chat_id=receive_linkable_telegram_channel_id(self.config),
                    text=ocr_text_translated
                )

    # llm картинки + ocr, оба в переводе
    async def handle_picture_message(self, chat_id, message_id, file_id, context: CallbackContext):
        image_file = await context.bot.get_file(file_id)
        image_as_bytearray = await image_file.download_as_bytearray()
        await context.bot.send_photo(
            chat_id=receive_linkable_telegram_channel_id(self.config),
            photo=image_file.file_id
        )
        pil_image = get_bytearray_photo_as_image(image_as_bytearray)
        await self._picture_message_process(pil_image, context)
        await context.bot.send_message(
            chat_id=chat_id,
            text="Картинка успешно обработана",
            reply_to_message_id=message_id
        )

    async def _video_or_gif_message_process(self, video_or_gif_file_id: str, context: CallbackContext):
        file = await context.bot.get_file(video_or_gif_file_id)
        video_or_gif_as_bytearray = await file.download_as_bytearray()
        await self._video_or_gif_as_bytearray_message_process(video_or_gif_as_bytearray, context)

    async def _video_or_gif_as_bytearray_message_process(
        self,
        video_or_gif_as_bytearray: bytearray,
        context: CallbackContext
    ):
        frames = extract_frames_from_begin_middle_end_video_bytearray(video_or_gif_as_bytearray)
        for frame in frames:
            await self._picture_message_process(frame, context)

    # то же, что и для картинки, но для нескольких кадров, + распознавание голоса?
    async def handle_video_message(self, chat_id, message_id, video_file_id, context: CallbackContext):
        await context.bot.send_video(chat_id=receive_linkable_telegram_channel_id(self.config), video=video_file_id)
        await self._video_or_gif_message_process(video_file_id, context)
        await context.bot.send_message(chat_id=chat_id, text="Видео успешно обработано", reply_to_message_id=message_id)

    # все же смысла нет переводить
    async def handle_text_message(self, chat_id, message_id, text, context: CallbackContext):
        await context.bot.send_message(
            chat_id=receive_linkable_telegram_channel_id(self.config),
            text=text
        )
        await context.bot.send_message(chat_id=chat_id, text="Текст переслан", reply_to_message_id=message_id)

    # то же, что для видео, но без распознавания голоса
    async def handle_gif_animation_message(
        self,
        chat_id: str,
        message_id: int,
        file_id: str,
        context: CallbackContext
    ):
        await context.bot.send_animation(chat_id=receive_linkable_telegram_channel_id(self.config), animation=file_id)
        await self._video_or_gif_message_process(file_id, context)
        await context.bot.send_message(chat_id=chat_id, text="Гифка успешно обработана", reply_to_message_id=message_id)

    # картинка, видео, гифка, отправленные в несжатом виде
    async def handle_attachment_message(
        self,
        chat_id: str,
        message_id: int,
        file_id: str,
        file_mime_type: str,
        context: CallbackContext
    ):
        file_meta = await context.bot.get_file(file_id)
        file_name = file_meta.file_path.split('/')[-1]
        file_as_bytearray = await file_meta.download_as_bytearray()

        # В зависимости от типа файла можно добавить логику обработки
        if file_mime_type.startswith("image/"):
            if file_mime_type == "image/gif":
                # TODO: Не работает, разобраться, почему, в будущем
                # await context.bot.send_animation(
                #     chat_id=receive_linkable_telegram_channel_id(self.config),
                #     animation=bytes(file_as_bytearray),
                #     filename=file_name,
                # )
                await context.bot.send_video(
                    chat_id=receive_linkable_telegram_channel_id(self.config),
                    video=bytes(file_as_bytearray),
                    filename=file_name,
                )
                await self._video_or_gif_message_process(file_id, context)
                await context.bot.send_message(
                    chat_id,
                    "Гифка успешно обработана",
                    reply_to_message_id=message_id
                )
            else:
                pil_image = get_bytearray_photo_as_image(file_as_bytearray)
                await context.bot.send_photo(
                    chat_id=receive_linkable_telegram_channel_id(self.config),
                    photo=bytes(file_as_bytearray),
                    filename=file_name
                )
                await self._picture_message_process(pil_image, context)
                await context.bot.send_message(
                    chat_id,
                    "Картинка успешно обработана",
                    reply_to_message_id=message_id
                )
        elif file_mime_type.startswith("video/"):
            await context.bot.send_video(
                chat_id=receive_linkable_telegram_channel_id(self.config),
                video=bytes(file_as_bytearray),
                filename=file_name
            )
            await self._video_or_gif_as_bytearray_message_process(file_as_bytearray, context)
            await context.bot.send_message(
                chat_id,
                "Видео успешно обработано",
                reply_to_message_id=message_id
            )
        else:
            await context.bot.send_message(
                chat_id,
                "Я не поддерживаю документ такого типа",
                reply_to_message_id=message_id
            )