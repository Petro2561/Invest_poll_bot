from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any, Dict, Final

from aiogram import F, Bot, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandObject
from aiogram.methods import PinChatMessage


from aiogram_dialog import DialogManager, StartMode

from bot.services.database.repositories.general import Repository
from bot.services.database.uow import UoW
from bot.telegram.dialogs.states import PollSG


if TYPE_CHECKING:
    from ...services.database import DBUser

router: Final[Router] = Router(name=__name__)


@router.message(CommandStart())
async def start_command(
    message: Message,
    user: DBUser,
    dialog_manager: DialogManager,
    repository: Repository,
    uow: UoW,
    bot: Bot,
    command: CommandObject,
) -> Any:
    """Обработчик команды /start с поддержкой реферальных ссылок"""
    user_id = user.id
    
    # Обработка реферальной ссылки
    ref_code = None
    if command.args:
        # Парсим реферальную ссылку вида /start ref_123
        if command.args.startswith("ref_"):
            try:
                ref_code = command.args
                referrer_id = int(command.args.replace("ref_", ""))
                
                # Проверяем, что это не самореферал
                if referrer_id != user_id:
                    # Сохраняем реферала
                    existing_referral = await repository.referrals.get_by_referred_id(user_id)
                    if not existing_referral:
                        await repository.referrals.create_referral(
                            referrer_id=referrer_id,
                            referred_id=user_id
                        )
                        await uow.commit()
                    
                    # Сохраняем referrer_id в пользователе
                    if not user.referrer_id:
                        user.referrer_id = referrer_id
                        await uow.commit(user)
            except (ValueError, Exception) as e:
                logging.error(f"Ошибка при обработке реферальной ссылки: {e}")
    
    # Если пользователь админ - показываем админ-меню
    if user.is_admin:
        pinned_message = await message.answer(text=templates.MAIN_MENU)
        await bot.pin_chat_message(chat_id=message.chat.id, message_id=pinned_message.message_id)
        await dialog_manager.start(state=MainMenuSG.main_menu, mode=StartMode.RESET_STACK)
        return
    
    # Если пользователь уже прошел опрос - показываем экран "уже участвуешь"
    if user.has_completed_poll:
        await dialog_manager.start(state=PollSG.already_completed, mode=StartMode.RESET_STACK)
        return
    
    # Иначе начинаем опрос с welcome экрана
    await dialog_manager.start(state=PollSG.welcome, mode=StartMode.RESET_STACK)


# @router.message(Command("support"))
# async def admin_command(message: Message, dialog_manager: DialogManager, user: DBUser) -> Any:
#     await message.answer(text="По всем вопросам пишите в поддержку @petro2561")
