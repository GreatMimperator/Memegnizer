import json

from telegram.ext import Application, CallbackContext, filters

from config.telegram_config import receive_telegram_bot_token
from redis_util.redis_queue_utils import RedisQueue
from redis_util.task_model import Task
from tg.task_processor import TaskProcessor


class TaskController:

    def __init__(self, config, redis_queue: RedisQueue):
        self.config = config
        self.redis_queue = redis_queue
        self.task_processor = TaskProcessor(config)
        self.application = Application.builder().token(receive_telegram_bot_token(self.config)).build()

    async def process_task(self, task: Task):
        """Обрабатывает задачу, извлеченную из Redis."""
        # Создаем контекст для сообщения, предполагая, что он будет доступен через chat_id и message_id
        context = CallbackContext(self.application, chat_id=task.chat_id, user_id=task.user_id)

        # Пример обработки в зависимости от типа фильтра
        if task.filter_type == filters.PHOTO.name:  # Проверка на тип фотографии
            await self.task_processor.handle_picture_message(task.chat_id, task.message_id, task.file_id, context)
        elif task.filter_type == filters.VIDEO.name:  # Проверка на тип видео
            await self.task_processor.handle_video_message(task.chat_id, task.message_id, task.file_id, context)
        elif task.filter_type == filters.TEXT.name:  # Проверка на тип текста
            await self.task_processor.handle_text_message(task.chat_id, task.message_id, task.text, context)
        elif task.filter_type == filters.ANIMATION.name:  # Проверка на тип анимации
            await self.task_processor.handle_gif_animation_message(task.chat_id, task.message_id, task.file_id, context)
        elif task.filter_type == filters.ATTACHMENT.name:  # Проверка на тип вложений
            await self.task_processor.handle_attachment_message(
                task.chat_id,
                task.message_id,
                task.file_id,
                task.mime_type,
                context
            )
        else:
            raise Exception(f"Неизвестный тип фильтра: {task.filter_type}")

    async def start(self):
        """Запуск процесса обработки задач из Redis"""
        while True:
            task: Task = self.redis_queue.dequeue()
            if task:
                await self.process_task(task)