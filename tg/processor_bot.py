from telegram.ext import Application, CallbackContext, filters

from config.telegram_config import receive_telegram_bot_token
from redis_util import RedisQueue
from tg.task_processor import TaskProcessor


class TaskController:

    def __init__(self, config, redis_queue: RedisQueue):
        self.config = config
        self.redis_queue = redis_queue
        self.task_processor = TaskProcessor(config)
        self.application = Application.builder().token(receive_telegram_bot_token(self.config)).build()

    async def process_task(self, task):
        """Обрабатывает задачу, извлеченную из Redis."""
        chat_id = task["chat_id"]
        user_id = task["user_id"]
        message_id = task["message_id"]
        file_id = task["file_id"]
        file_mime_type = task["mime_type"]
        filter_type = task["filter_type"]
        text = task["text"]

        # Создаем контекст для сообщения, предполагая, что он будет доступен через chat_id и message_id
        context = CallbackContext(self.application, chat_id=chat_id, user_id=user_id)

        # Пример обработки в зависимости от типа фильтра
        if filter_type == filters.PHOTO.name:  # Проверка на тип фотографии
            await self._process_photo(chat_id, message_id, file_id, context)
        elif filter_type == filters.VIDEO.name:  # Проверка на тип видео
            await self._process_video(chat_id, message_id, file_id, context)
        elif filter_type == filters.TEXT.name:  # Проверка на тип текста
            await self._process_text(chat_id, message_id, text, context)
        elif filter_type == filters.ANIMATION.name:  # Проверка на тип анимации
            await self._process_gif(chat_id, message_id, file_id, context)
        elif filter_type == filters.ATTACHMENT.name:  # Проверка на тип вложений
            await self._process_attachment(chat_id, message_id, file_id, file_mime_type, context)
        else:
            raise Exception(f"Неизвестный тип фильтра: {filter_type}")

    async def _process_photo(self, chat_id, message_id, file_id, context):
        # Задача для обработки фотографии
        await self.task_processor.handle_picture_message(chat_id, message_id, file_id, context)

    async def _process_video(self, chat_id, message_id, file_id, context):
        # Задача для обработки видео
        await self.task_processor.handle_video_message(chat_id, message_id, file_id, context)

    async def _process_text(self, chat_id, message_id, text, context):
        await self.task_processor.handle_text_message(chat_id, message_id, text, context)

    async def _process_gif(self, chat_id, message_id, file_id, context):
        # Задача для обработки гифки
        await self.task_processor.handle_gif_animation_message(chat_id, message_id, file_id, context)

    async def _process_attachment(self, chat_id, message_id, file_id, file_mime_type, context):
        await self.task_processor.handle_attachment_message(chat_id, message_id, file_id, file_mime_type, context)

    async def start(self):
        """Запуск процесса обработки задач из Redis"""
        while True:
            task = self.redis_queue.dequeue()
            if task:
                await self.process_task(task)