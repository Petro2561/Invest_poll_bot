from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.ext.asyncio import async_sessionmaker

from ...services.database import Repository, UoW, SQLSessionContext


class DBSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: async_sessionmaker) -> None:
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        async with SQLSessionContext(session_pool=self.session_pool) as (
            repository,
            uow
        ):
            data["repository"] = repository
            data["uow"] = uow
            return await handler(event, data)
