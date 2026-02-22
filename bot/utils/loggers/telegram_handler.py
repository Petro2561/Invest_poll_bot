from logging import Handler, LogRecord
import asyncio
from aiogram import Bot
import logging


class TelegramLogHandler(Handler):
    def __init__(self, bot_token: str, chat_id: int, level=logging.ERROR):
        super().__init__(level)
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    def emit(self, record: LogRecord) -> None:
        try:
            log_entry = self.format(record)
            asyncio.create_task(self.send_message(log_entry))
        except Exception:
            self.handleError(record)

    async def send_message(self, message: str):
        try:
            await self.bot.send_message(chat_id=self.chat_id, text=f"🚨 Лог:\n<pre>{message}</pre>", parse_mode="HTML")
        except Exception as e:
            print(f"[TelegramLogHandler] Ошибка при отправке: {e}")
