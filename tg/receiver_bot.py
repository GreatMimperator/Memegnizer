import json

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

from config.telegram_config import receive_telegram_bot_token, receive_telegram_admin_id
from redis_util.redis_queue_utils import RedisQueue
from redis_util.task_model import Task


class MessageReceiver:

    def __init__(self, config, redis_queue: RedisQueue):
        self.config = config
        self.redis_queue = redis_queue

    async def handle_message(self, update: Update, context: CallbackContext):
        """Обработчик всех типов сообщений с добавлением фильтров."""
        message = update.message
        if message.from_user.id != receive_telegram_admin_id(self.config):
            await message.reply_text("Вы не являетесь админом")
            pass
        task = Task()
        task.chat_id = message.chat_id
        task.message_id = message.message_id

        # Проверка типа фильтра на основе типа сообщения
        if message.photo:
            task.filter_type = filters.PHOTO.name
            task.file_id = message.photo[-1].file_id
        elif message.video:
            task.filter_type = filters.VIDEO.name
            task.file_id = message.video.file_id
        elif message.animation:
            task.filter_type = filters.ANIMATION.name
            task.file_id = message.animation.file_id
        elif message.document:
            task.filter_type = filters.ATTACHMENT.name
            document = message.document
            task.mime_type = document.mime_type
            task.file_id = document.file_id
        elif message.text:
            task.filter_type = filters.TEXT.name
        else:
            await message.reply_text("Я не поддерживаю такие сообщения", reply_to_message_id=message.message_id)
            return

        self.redis_queue.enqueue(task)

    def start(self):
        """Запуск бота для получения сообщений"""
        bot_token = receive_telegram_bot_token(self.config)
        application = Application.builder().token(bot_token).build()

        application.add_handler(MessageHandler(filters.ALL, self.handle_message))

        application.run_polling()