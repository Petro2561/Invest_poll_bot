from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram_dialog import setup_dialogs
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..config import Config
from ..middlewares import DBSessionMiddleware, UserMiddleware, DialogMiddleware
from ..utils import msgspec_json as mjson
from bot.telegram.dialogs import router

if TYPE_CHECKING:
    from bot.telegram.dialogs.scheduler import MessageScheduler


def _setup_outer_middlewares(
    dispatcher: Dispatcher,
    session_pool: async_sessionmaker,
    config: Config,
    bot: Bot,
    redis: Redis,
    scheduler: "MessageScheduler | None" = None
) -> None:
    dispatcher.update.outer_middleware(DBSessionMiddleware(session_pool=session_pool))
    dispatcher.update.outer_middleware(UserMiddleware())
    dispatcher.update.outer_middleware(
        DialogMiddleware(
            config=config,
            bot=bot,
            scheduler=scheduler,
            redis=redis
        )
    )


def _setup_inner_middlewares(dispatcher: Dispatcher) -> None:
    # dispatcher.callback_query.middleware(CallbackAnswerMiddleware())
    pass


def create_dispatcher(
    config: Config,
    session_pool: async_sessionmaker,
    redis: Redis,
    bot: Bot,
    scheduler: "MessageScheduler | None" = None
) -> Dispatcher:
    """
    :return: Configured ``Dispatcher`` with installed middlewares and included routers
    """
    dispatcher: Dispatcher = Dispatcher(
        name="main_dispatcher",
        storage=RedisStorage(
            redis=redis,
            json_loads=mjson.decode,
            json_dumps=mjson.encode,
            key_builder=DefaultKeyBuilder(with_destiny=True),
        ),
        config=config,
    )
    dispatcher.include_routers(router)
    setup_dialogs(dispatcher)

    _setup_outer_middlewares(
        dispatcher=dispatcher,
        session_pool=session_pool,
        config=config,
        bot=bot,
        redis=redis,
        scheduler=scheduler
    )
    _setup_inner_middlewares(dispatcher=dispatcher)
    return dispatcher
