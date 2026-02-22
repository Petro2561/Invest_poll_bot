import logging
from datetime import datetime, timedelta

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.date import DateTrigger

logger: logging.Logger = logging.getLogger(__name__)


async def _send_scheduled_message(
    bot_token: str,
    user_id: int,
    message_text: str
) -> None:
    """Отправить запланированное сообщение пользователю"""
    try:
        # Создаем новый экземпляр Bot для отправки сообщения
        bot = Bot(token=bot_token)
        await bot.send_message(
            chat_id=user_id,
            text=message_text,
            parse_mode="HTML"
        )
        await bot.session.close()
        logger.info(f"Сообщение отправлено пользователю {user_id}")
    except Exception as e:
        logger.error(
            f"Ошибка при отправке сообщения пользователю {user_id}: {e}"
        )


class MessageScheduler:
    """Планировщик для отправки сообщений через 24 часа"""

    def __init__(self, url: str, timezone: str, bot_token: str):
        self.url = url
        self.timezone = timezone
        self.bot_token = bot_token
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': SQLAlchemyJobStore(url=self.url)},
            timezone=timezone
        )

    async def schedule_message(
        self,
        user_id: int,
        message_text: str,
        minutes: int = 1
        # hours: int = 24
    ) -> str:
        """
        Запланировать отправку сообщения через указанное количество часов

        Args:
            user_id: ID пользователя для отправки
            message_text: Текст сообщения
            minutes: Количество минут до отправки (по умолчанию 1)

        Returns:
            job_id: ID созданной задачи
        """
        # Вычисляем время отправки
        # send_time = datetime.now() + timedelta(hours=hours)
        send_time = datetime.now() + timedelta(minutes=minutes)

        # Создаем уникальный ID задачи
        job_id = f"reminder_{user_id}_{int(send_time.timestamp())}"

        try:
            self.scheduler.add_job(
                func=_send_scheduled_message,
                trigger=DateTrigger(run_date=send_time),
                args=[self.bot_token, user_id, message_text],
                id=job_id,
                replace_existing=True,
                jobstore='default'
            )
            logger.info(
                f"Сообщение для пользователя {user_id} запланировано "
                f"на {send_time}, job_id: {job_id}"
            )
            return job_id
        except Exception as e:
            logger.error(f"Ошибка при планировании сообщения: {e}")
            return ""

    async def remove_job(self, job_id: str) -> None:
        """Удалить задачу по ID"""
        try:
            self.scheduler.remove_job(job_id=job_id, jobstore='default')
            logger.info(f"Задача {job_id} удалена из планировщика")
        except Exception as e:
            logger.error(f"Ошибка при удалении задачи {job_id}: {e}")

    async def start_scheduler(self) -> None:
        """Запустить планировщик"""
        self.scheduler.start()
        logger.info("Планировщик запущен")

    async def shutdown_scheduler(self) -> None:
        """Остановить планировщик"""
        self.scheduler.shutdown()
        logger.info("Планировщик остановлен")


async def send_long_message(bot: Bot, chat_id: int, text: str, **kwargs):
    """
    Отправка длинного HTML-сообщения без обрыва тегов.
    """
    while text:
        if len(text) <= 4096:
            await bot.send_message(chat_id=chat_id, text=text, **kwargs)
            break

        chunk = text[:4096]
        last_open = chunk.rfind("<")
        last_close = chunk.rfind(">")
        if last_open > last_close:
            chunk = chunk[:last_open]

        await bot.send_message(chat_id=chat_id, text=chunk, **kwargs)
        text = text[len(chunk):]
