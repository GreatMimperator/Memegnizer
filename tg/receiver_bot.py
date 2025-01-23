import json

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from config.telegram_config import receive_telegram_bot_token
from redis_util import RedisQueue


class MessageReceiver:

    def __init__(self, config, redis_queue: RedisQueue):
        self.config = config
        self.redis_queue = redis_queue

    async def handle_message(self, update: Update, context: CallbackContext):
        """Обработчик всех типов сообщений с добавлением фильтров."""
        message = update.message
        chat_id = message.chat.id
        message_id = message.message_id

        mime_type = None
        file_id = None
        # Проверка типа фильтра на основе типа сообщения
        if message.photo:
            filter_type = filters.PHOTO.name
            file_id = message.photo[-1].file_id
        elif message.video:
            filter_type = filters.VIDEO.name
            file_id = message.video.file_id
        elif message.animation:
            filter_type = filters.ANIMATION.name
            file_id = message.animation.file_id
        elif message.document:
            filter_type = filters.ATTACHMENT.name
            document = message.document
            mime_type = document.mime_type
            file_id = document.file_id
        elif message.text:
            filter_type = filters.TEXT.name
        else:
            await message.reply_text("Я не поддерживаю такие сообщения", reply_to_message_id=message_id)
            return

        task = {
            "chat_id": chat_id,
            "user_id": update.message.from_user.id,
            "message_id": message_id,
            "file_id": file_id,
            "filter_type": filter_type,
            "mime_type": mime_type,
            "text": message.text,
        }
        self.redis_queue.enqueue(task)

    def start(self):
        """Запуск бота для получения сообщений"""
        bot_token = receive_telegram_bot_token(self.config)
        application = Application.builder().token(bot_token).build()

        application.add_handler(MessageHandler(filters.ALL, self.handle_message))

        application.run_polling()