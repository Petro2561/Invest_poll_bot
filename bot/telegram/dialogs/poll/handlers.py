"""Обработчики для диалога опроса"""
import logging
from typing import TYPE_CHECKING

from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Button

from bot.services.database.repositories.general import Repository
from bot.services.database.uow import UoW
from bot.telegram.dialogs.states import PollSG
from bot.config import Config

if TYPE_CHECKING:
    from bot.services.database import DBUser


async def on_start_poll_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Начать опрос'"""
    user_id = callback.from_user.id
    config: Config = manager.middleware_data["config"]
    bot: Bot = manager.middleware_data["bot"]

    # Проверяем подписку на канал
    channel_username = config.expert_channel.channel_username.lstrip("@")
    try:
        member = await bot.get_chat_member(
            chat_id=f"@{channel_username}",
            user_id=user_id
        )
        is_subscribed = member.status in ["member", "administrator", "creator"]
    except Exception:
        is_subscribed = False

    if not is_subscribed:
        await manager.switch_to(PollSG.subscription_required)
    else:
        await manager.switch_to(PollSG.start_poll)


async def on_subscription_check_click(
    callback: CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Я подписался'"""
    user_id = callback.from_user.id
    config: Config = dialog_manager.middleware_data["config"]
    bot: Bot = dialog_manager.middleware_data["bot"]
    channel_username = config.expert_channel.channel_username

    try:
        member = await bot.get_chat_member(
            chat_id=channel_username,
            user_id=user_id
        )
        if member.status in ["left", "kicked"]:
            await callback.answer(
                "Вы не подписаны на наш канал 😉️️️️️️",
                show_alert=True
            )
        else:
            await dialog_manager.switch_to(
                state=PollSG.question,
                show_mode=ShowMode.SEND
            )
    except Exception as error:
        logging.error(f"Ошибка проверки группы {error}")
        await dialog_manager.switch_to(
            state=PollSG.question,
            show_mode=ShowMode.SEND
        )

# async def check_rights_to_generate(user: DBUser, repository: Repository):
#     db_user = await repository.users.get(user_id=user.user_id)
#     if db_user:
#         if db_user.is_admin:
#             return True
#         if db_user.numbers_of_generates < settings.NUMBER_OF_GENERATES:
#             return True
#     return False


async def on_continue_poll_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Продолжить' после напоминания"""
    # Переходим к текущему вопросу (на основе questions_completed)
    await manager.switch_to(PollSG.question)


async def on_answer_selected(
    callback: CallbackQuery,
    widget,
    manager: DialogManager,
    item_id: str,
) -> None:
    """Обработчик выбора ответа на вопрос"""
    repository: Repository = manager.middleware_data["repository"]
    user: "DBUser" = manager.middleware_data["user"]
    user_id = user.id

    # Получаем актуальные данные пользователя из БД
    fresh_user = await repository.users.get(user_id)
    if not fresh_user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    # Получаем все опросы
    polls = await repository.polls.get_all()
    if not polls:
        await callback.answer("Опрос не найден", show_alert=True)
        return

    # Получаем текущий опрос на основе количества пройденных вопросов из БД
    questions_completed = fresh_user.questions_completed
    total_questions = len(polls)

    # Если все вопросы пройдены, берем последний
    if questions_completed >= total_questions:
        poll = polls[-1]
    else:
        poll = polls[questions_completed]

    selected_answer_num = int(item_id)  # Номер выбранного ответа (1-8)

    # Получаем текст выбранного ответа
    answer_text = repository.polls.get_answer_text(poll, selected_answer_num)
    if not answer_text:
        await callback.answer("Ответ не найден", show_alert=True)
        return

    # Проверяем правильность ответа
    is_correct = selected_answer_num == poll.correct_answer

    # Если это 5-й вопрос (questions_completed == 4, следующий будет 5-й)
    # и ответ правильный, удаляем напоминание
    if questions_completed == 4 and is_correct:
        scheduler = manager.middleware_data.get("scheduler")
        redis = manager.middleware_data.get("redis")

        if scheduler and redis:
            reminder_key = f"poll_reminder:{user_id}"
            job_id = await redis.get(reminder_key)
            if job_id:
                job_id_str = (
                    job_id.decode('utf-8')
                    if isinstance(job_id, bytes)
                    else job_id
                )
                await scheduler.remove_job(job_id_str)
                await redis.delete(reminder_key)
                logging.info(
                    f"Напоминание для пользователя {user_id} "
                    f"удалено (job_id: {job_id_str})"
                )

    # Сохраняем данные в dialog_data
    manager.dialog_data["current_poll_id"] = poll.id
    manager.dialog_data["user_answer"] = answer_text
    manager.dialog_data["is_correct"] = is_correct

    # Всегда показываем экран с обратной связью
    await manager.switch_to(PollSG.answer_feedback)


async def on_retry_question_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Попробовать снова'"""
    await manager.switch_to(PollSG.question)


async def on_continue_after_correct_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Идем дальше' после правильного ответа"""
    repository: Repository = manager.middleware_data["repository"]
    uow: UoW = manager.middleware_data["uow"]
    user: "DBUser" = manager.middleware_data["user"]
    user_id = user.id

    # Получаем актуальные данные пользователя из БД
    fresh_user = await repository.users.get(user_id)
    if not fresh_user:
        await callback.answer("Пользователь не найден", show_alert=True)
        return

    # Получаем все опросы
    polls = await repository.polls.get_all()
    total_questions = len(polls)

    # Увеличиваем количество пройденных вопросов
    fresh_user.questions_completed += 1
    await uow.commit(fresh_user)

    # Проверяем, завершен ли опрос
    if fresh_user.questions_completed >= total_questions:
        # Завершаем опрос
        fresh_user.has_completed_poll = True
        await uow.commit(fresh_user)

        # Если пользователь пришел по реферальной ссылке,
        # помечаем реферала как завершенного
        if fresh_user.referrer_id:
            referral = await repository.referrals.get_by_referred_id(user_id)
            if referral and not referral.is_completed:
                await repository.referrals.mark_completed(user_id)
                await uow.commit()

        await manager.switch_to(PollSG.poll_completed)
    elif fresh_user.questions_completed == 4:
        # Показываем промежуточное окно после 4-го вопроса
        # Создаем напоминание через 24 часа
        scheduler = manager.middleware_data.get("scheduler")
        redis = manager.middleware_data.get("redis")

        if scheduler and redis:
            reminder_text = (
                "Привет! Ты остановился на 4-м вопросе. "
                "Продолжи опрос, чтобы участвовать в розыгрыше "
                "поездки в Дубай! ✈️🇦🇪"
            )
            job_id = await scheduler.schedule_message(
                user_id=user_id,
                message_text=reminder_text,
                minutes=1
                # hours=24
            )
            if job_id:
                # Сохраняем job_id в Redis
                reminder_key = f"poll_reminder:{user_id}"
                await redis.set(
                    reminder_key, job_id, ex=86400 * 2
                )  # 2 дня TTL

        await manager.switch_to(PollSG.mid_poll_reminder)
    else:
        # Переходим к следующему вопросу
        await manager.switch_to(PollSG.question)


async def on_increase_chances_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Увеличить шансы'"""
    await manager.switch_to(PollSG.referral_screen)


async def on_leave_as_is_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Оставить как есть'"""
    await manager.switch_to(PollSG.referral_screen)


async def on_share_bot_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Поделиться ботом'"""
    bot: Bot = manager.middleware_data["bot"]
    user_id = callback.from_user.id
    ref_code = f"ref_{user_id}"
    bot_username = (
        bot.username if hasattr(bot, 'username') and bot.username
        else "your_bot"
    )
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"

    await callback.answer(
        f"Ваша реферальная ссылка: {ref_link}",
        show_alert=True
    )


async def on_my_chances_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Мои шансы'"""
    await manager.switch_to(PollSG.my_chances)


async def on_invite_more_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Пригласить еще'"""
    await manager.switch_to(PollSG.referral_screen)


async def on_back_from_chances_click(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    """Обработчик кнопки 'Назад' из экрана шансов"""
    await manager.switch_to(PollSG.referral_screen)
