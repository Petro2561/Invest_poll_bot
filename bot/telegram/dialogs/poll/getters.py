"""Геттеры для диалога опроса"""
from typing import TYPE_CHECKING, Any

from aiogram import Bot
from aiogram_dialog import DialogManager

if TYPE_CHECKING:
    from bot.services.database import Repository
    from bot.services.database.models import DBUser


async def get_subscription_data(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, Any]:
    """Получить данные для экрана подписки на канал"""
    config = dialog_manager.middleware_data["config"]
    bot: Bot = dialog_manager.middleware_data["bot"]
    user_id = dialog_manager.event.from_user.id
    
    channel_username = config.expert_channel.channel_username.lstrip("@")
    channel_url = f"https://t.me/{channel_username}"
    
    # Проверяем подписку на канал
    is_subscribed = False
    try:
        member = await bot.get_chat_member(
            chat_id=f"@{channel_username}",
            user_id=user_id
        )
        is_subscribed = member.status in ["member", "administrator", "creator"]
    except Exception:
        is_subscribed = False

    return {
        "channel_url": channel_url,
        "is_subscribed": is_subscribed,
        "not_subscribed": not is_subscribed,  # Для условия when
    }


async def get_current_question(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, Any]:
    """Получить текущий опрос в зависимости от
    количества пройденных вопросов"""
    repository: "Repository" = dialog_manager.middleware_data["repository"]
    user: "DBUser" = dialog_manager.middleware_data["user"]
    user_id = user.id

    # Получаем актуальные данные пользователя из БД
    fresh_user = await repository.users.get(user_id)
    if not fresh_user:
        return {
            "question": None,
            "question_text": "Пользователь не найден",
            "answer_options": [],
            "is_last": True,
            "question_number": 0,
            "total_questions": 0,
        }

    # Получаем все опросы
    polls = await repository.polls.get_all()
    if not polls:
        return {
            "question": None,
            "question_text": "Опрос не найден",
            "answer_options": [],
            "is_last": True,
            "question_number": 0,
            "total_questions": 0,
        }

    # Получаем текущий вопрос на основе количества пройденных вопросов из БД
    questions_completed = fresh_user.questions_completed
    total_questions = len(polls)

    # Если все вопросы пройдены, возвращаем последний
    if questions_completed >= total_questions:
        poll = polls[-1]
        is_last = True
    else:
        poll = polls[questions_completed]
        is_last = questions_completed == total_questions - 1

    # Получаем все ответы опроса
    all_answers = repository.polls.get_all_answers(poll)
    answer_options = [
        {"id": str(answer_num), "text": answer_text}
        for answer_num, answer_text in all_answers
    ]

    return {
        "question": poll,
        "question_text": poll.question_text,
        "answer_options": answer_options,
        "is_last": is_last,
        "poll_id": poll.id,
        "hint": poll.hint or "",
        "question_number": questions_completed + 1,
        "total_questions": total_questions,
    }


async def get_answer_feedback(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, Any]:
    """Получить информацию о правильности
    ответа"""
    poll_id = dialog_manager.dialog_data.get("current_poll_id")
    user_answer = dialog_manager.dialog_data.get("user_answer", "")
    is_correct = dialog_manager.dialog_data.get("is_correct", False)

    repository: "Repository" = dialog_manager.middleware_data["repository"]
    config = dialog_manager.middleware_data["config"]

    # По умолчанию данных по вопросу нет
    hint = ""
    poll_link = ""
    correct_reaction = ""

    if poll_id:
        poll = await repository.polls.get_by_id(poll_id)
        if poll:
            hint = poll.hint or ""
            poll_link = poll.link or ""
            correct_reaction = poll.correct_answer_reaction or ""

    # Формируем текст ответа в зависимости от правильности
    from bot.telegram.dialogs.poll import templates
    if is_correct:
        answer_text = correct_reaction or templates.CORRECT_ANSWER_TEXT
    else:
        # Если подсказка есть — используем шаблон с подсказкой,
        # если нет — показываем только текст без блока "Подсказка",
        # но с фразой "Эксперт разбирал этот вопрос в своем канале"
        if hint:
            answer_text = templates.INCORRECT_ANSWER_TEXT.format(hint=hint)
        else:
            answer_text = (
                "Не совсем\n\n"
                "Эксперт разбирал этот вопрос в своем канале"
            )

    # Получаем URL канала эксперта
    channel_username = config.expert_channel.channel_username.lstrip("@")
    channel_url = f"https://t.me/{channel_username}"
    target_url = poll_link or channel_url

    return {
        "is_correct": is_correct,
        "not_is_correct": not is_correct,  # Для условия when="~is_correct"
        "hint": hint,
        "user_answer": user_answer,
        "answer_text": answer_text,
        "channel_url": target_url,
    }


async def get_poll_completed_data(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, Any]:
    """Получить данные после завершения опроса"""
    repository: "Repository" = dialog_manager.middleware_data["repository"]
    bot: Bot = dialog_manager.middleware_data["bot"]
    user_id = dialog_manager.event.from_user.id

    ref_code = f"ref_{user_id}"
    bot_info = await bot.get_me()
    bot_username = bot_info.username
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"

    # Базовый шанс = 1
    base_chances = 1

    # Подсчитываем рефералов
    referrals_count = await repository.referrals.count_completed_referrals(
        user_id
    )
    total_chances = base_chances + referrals_count

    return {
        "chances": total_chances,
        "ref_link": ref_link,
        "ref_code": ref_code,
    }


async def get_referral_data(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, Any]:
    """Получить данные для реферального экрана"""
    user_id = dialog_manager.event.from_user.id

    # Создаем реферальный код для inline query
    ref_code = f"ref_{user_id}"
    bot: Bot = dialog_manager.middleware_data["bot"]
    me = await bot.get_me()
    bot_username = me.username
    ref_link = f"https://t.me/{bot_username}?start={ref_code}"

    return {
        "ref_link": ref_link,
        "ref_code": ref_code,
    }


async def get_my_chances_data(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, Any]:
    """Получить данные о шансах пользователя"""
    repository: "Repository" = dialog_manager.middleware_data["repository"]
    user_id = dialog_manager.event.from_user.id

    referrals_count = await repository.referrals.count_completed_referrals(
        user_id
    )
    total_chances = 1 + referrals_count

    return {
        "referrals_count": referrals_count,
        "total_chances": total_chances,
    }


async def get_already_completed_data(
    dialog_manager: DialogManager, **kwargs
) -> dict[str, Any]:
    """Получить данные для пользователя,
    который уже прошел опрос"""
    repository: "Repository" = dialog_manager.middleware_data["repository"]
    user_id = dialog_manager.event.from_user.id

    referrals_count = await repository.referrals.count_completed_referrals(
        user_id
    )
    total_chances = 1 + referrals_count

    # Создаем реферальный код для inline query
    ref_code = f"ref_{user_id}"

    return {
        "chances": total_chances,
        "ref_code": ref_code,
    }
