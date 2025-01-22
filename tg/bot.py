import easyocr
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters

from config.telegram_config import receive_telegram_bot_token
from ocr.meme_ocr_receiver import ocr_image
from tg.content_util import get_message_photo_as_image, get_bytearray_photo_as_image
from tools.llm import ollama_kit
from translate.prompt_translator import translate_from_to_ru
from util.media_util import convert_to_jpg_bytes, extract_frames_from_begin_middle_end_video_bytearray


class Bot:

    def __init__(self, config):
        self.config = config
        self.ocr_reader = easyocr.Reader(['ru', 'en'], gpu=False) # loads in memory once

    async def handle_start(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Привет, я бот, распознающий мемы и складывающий их описания в специальный канал")

    async def picture_message_process(self, pil_image: Image, update: Update):
        jpg_image_bytes = convert_to_jpg_bytes(pil_image)
        image_description = ollama_kit.ollama_image_describe(jpg_image_bytes, self.config)
        translated_image_description = translate_from_to_ru(image_description)
        await update.message.reply_text(translated_image_description)
        ocr_text = ocr_image(pil_image, self.ocr_reader)
        if len(ocr_text) > 1: # может возвращать один символ, например кавычку - нам это не нужно
            await update.message.reply_text(ocr_text)
            ocr_text_translated = translate_from_to_ru(ocr_text)
            if ocr_text_translated is not None and len(ocr_text_translated) > 1:
                await update.message.reply_text(ocr_text_translated)

    # llm картинки + ocr, оба в переводе
    async def handle_picture_message(self, update: Update, context: CallbackContext):
        pil_image = await get_message_photo_as_image(update)
        await self.picture_message_process(pil_image, update)

    async def video_or_gif_message_process(self, video_or_gif_file_id: str, update: Update, context: CallbackContext):
        file = await context.bot.get_file(video_or_gif_file_id)
        video_or_gif_as_bytearray = await file.download_as_bytearray()
        await self.video_or_gif_as_bytearray_message_process(video_or_gif_as_bytearray, update)

    async def video_or_gif_as_bytearray_message_process(
        self,
        video_or_gif_as_bytearray: bytearray,
        update: Update
    ):
        frames = extract_frames_from_begin_middle_end_video_bytearray(video_or_gif_as_bytearray)
        for frame in frames:
            await self.picture_message_process(frame, update)

    # то же, что и для картинки, но для нескольких кадров, + распознавание голоса?
    async def handle_video_message(self, update: Update, context: CallbackContext):
        await self.video_or_gif_message_process(update.message.video.file_id, update, context)

    # Переводим и все, можно постить
    async def handle_text_message(self, update: Update, context: CallbackContext):
        await update.message.reply_text(update.message.text)

    # то же, что для видео, но без распознавания голоса
    async def handle_gif_animation_message(self, update: Update, context: CallbackContext):
        await self.video_or_gif_message_process(update.message.animation.file_id, update, context)

    # картинка, видео, гифка, отправленные в несжатом виде
    async def handle_attachment_message(self, update: Update, context: CallbackContext):
        file = update.message.document

        mime_type = file.mime_type
        file_id = file.file_id

        file_meta = await context.bot.get_file(file_id)
        file_as_bytearray = await file_meta.download_as_bytearray()

        # В зависимости от типа файла можно добавить логику обработки
        if mime_type.startswith("image/"):
            if mime_type == "image/gif":
                await self.video_or_gif_message_process(file_id, update, context)
            else:
                pil_image = get_bytearray_photo_as_image(file_as_bytearray)
                await self.picture_message_process(pil_image, update)
        elif mime_type.startswith("video/"):
            await self.video_or_gif_as_bytearray_message_process(file_as_bytearray, update)
        else:
            await update.message.reply_text("Я не поддерживаю документ такого типа")

    # любое другое сообщение
    async def handle_unsupported_message(self, update: Update, context: CallbackContext):
        await update.message.reply_text("Я не поддерживаю такие сообщения")

    def start(self):
        bot_token = receive_telegram_bot_token(self.config)
        application = Application.builder().token(bot_token).build()

        application.add_handler(CommandHandler("start", self.handle_start))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_picture_message))
        application.add_handler(MessageHandler(filters.VIDEO, self.handle_video_message))
        application.add_handler(MessageHandler(filters.TEXT, self.handle_text_message))
        application.add_handler(MessageHandler(filters.ANIMATION, self.handle_gif_animation_message))
        application.add_handler(MessageHandler(filters.ATTACHMENT, self.handle_attachment_message))
        application.add_handler(MessageHandler(filters.ALL, self.handle_unsupported_message))

        application.run_polling()
