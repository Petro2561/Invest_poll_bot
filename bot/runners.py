from __future__ import annotations

from typing import TYPE_CHECKING

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from bot.telegram.dialogs.scheduler import MessageScheduler


if TYPE_CHECKING:
    from .config import Config


async def polling_startup(
    bots: list[Bot],
    config: "Config",
    dispatcher: Dispatcher
) -> None:
    scheduler = MessageScheduler(
        url=config.scheduler.url,
        timezone=config.scheduler.timezone,
        bot_token=config.tg_bot.token
    )
    await scheduler.start_scheduler()
    dispatcher.workflow_data["scheduler"] = scheduler

    # Обновляем DialogMiddleware с scheduler
    from bot.middlewares.outer.dialog import DialogMiddleware
    for middleware in dispatcher.update.outer_middleware:
        if isinstance(middleware, DialogMiddleware):
            middleware.scheduler = scheduler


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start', description='Перезапуск')
    ]
    await bot.set_my_commands(main_menu_commands)


def run_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher.startup.register(polling_startup)
    dispatcher.startup.register(set_main_menu)
    return dispatcher.run_polling(bot)
