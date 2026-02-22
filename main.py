import asyncio
import logging
import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs

from redis.asyncio import ConnectionPool, Redis

from bot.config import Config, load_config
from bot.telegram.dialogs.start import router
from bot.telegram.dialogs import router as start_dialog
from bot.middlewares.middleware import CheckUserMiddleware, DBSessionMiddleware
from bot.runners import run_polling


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    config: Config = load_config()
    bot = Bot(
        token=config.tg_bot.token, default=DefaultBotProperties(parse_mode="HTML")
    )
    redis: Redis = Redis(
        connection_pool=ConnectionPool(
            host=config.redis.host,
            port=config.redis.port,
            db=config.redis.db,
        )
    )
    dp: Dispatcher = Dispatcher(
        name="main_dispatcher",
        storage=RedisStorage(
            redis=redis, key_builder=DefaultKeyBuilder(with_destiny=True)
        ),
        config=config,
        redis=redis
    )

    setup_dialogs(dp)
    dp.include_router(router)
    dp.update.middleware(DBSessionMiddleware())
    dp.update.middleware(CheckUserMiddleware())
    asyncio.run(run_polling(dp, bot))


if __name__ == "__main__":
    main()
