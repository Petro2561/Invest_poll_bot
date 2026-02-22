from typing import Any, Awaitable, Callable, TYPE_CHECKING

from aiogram import BaseMiddleware, Bot
from aiogram.types import TelegramObject

from ...config import Config
from ...telegram.dialogs.scheduler import MessageScheduler

if TYPE_CHECKING:
    from redis.asyncio import Redis


class DialogMiddleware(BaseMiddleware):
    def __init__(
        self,
        config: Config,
        bot: Bot,
        scheduler: MessageScheduler | None = None,
        redis: "Redis | None" = None
    ) -> None:
        self.config = config
        self.bot = bot
        self.scheduler = scheduler
        self.redis = redis

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Добавляем в data для доступа через middleware_data в dialog_manager
        data["config"] = self.config
        data["bot"] = self.bot
        if self.scheduler:
            data["scheduler"] = self.scheduler
        if self.redis:
            data["redis"] = self.redis
        return await handler(event, data)
