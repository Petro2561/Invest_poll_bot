import logging

from bot.config import load_config

from .multiline import MultilineLogger
from bot.utils.loggers.telegram_handler import TelegramLogHandler


__all__ = ["database", "setup_logger", "MultilineLogger"]

database: logging.Logger = logging.getLogger("bot.database")



def setup_logger(level: int = logging.INFO) -> None:
    for name in ["aiogram.middlewares", "aiogram.event", "aiohttp.access"]:
        logging.getLogger(name).setLevel(logging.WARNING)

    logging.basicConfig(
        format="%(asctime)s %(levelname)s | %(name)s: %(message)s",
        datefmt="[%H:%M:%S]",
        level=level,
    )

    config = load_config()
    telegram_handler = TelegramLogHandler(
        bot_token=config.tg_bot.token,
        chat_id=65986858,
        level=logging.WARNING
    )
    telegram_handler.setFormatter(logging.Formatter("%(asctime)s | %(levelname)s | %(message)s"))
    logging.getLogger().addHandler(telegram_handler)

