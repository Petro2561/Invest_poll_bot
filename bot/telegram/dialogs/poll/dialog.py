"""Диалог инвестиционного опроса"""
from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import (
    Button,
    Column,
    SwitchTo,
    Group,
    Select,
    SwitchInlineQuery,
    Url,
)

from bot.telegram.dialogs.poll import templates, handlers, getters
from bot.telegram.dialogs.states import PollSG


poll_dialog = Dialog(
    # Welcome screen
    Window(
        Const(templates.WELCOME_TEXT),
        Button(
            Const("Начать опрос"),
            id="start_poll",
            on_click=handlers.on_start_poll_click,
        ),
        state=PollSG.welcome,
    ),

    # Проверка подписки
    Window(
        Const(templates.SUBSCRIPTION_REQUIRED_TEXT),
        Group(
            Button(
                Const("Подписаться на канал"),
                id="subscribe_channel",
                on_click=handlers.on_subscribe_channel_click,
            ),
            Button(
                Const("Я подписался"),
                id="check_subscription",
                on_click=handlers.on_subscription_check_click,
            ),
        ),
        state=PollSG.subscription_required,
    ),
    Window(
        Format(templates.QUESTION_TEXT),
        Column(
            Select(
                Format("{item[text]}"),
                id="answer_select",
                items="answer_options",
                item_id_getter=lambda item: str(item["id"]),
                on_click=handlers.on_answer_selected,
            ),
        ),
        getter=getters.get_current_question,
        state=PollSG.question,
    ),

    Window(
        Format("{answer_text}"),
        Button(
            Const("Идем дальше"),
            id="continue_after_correct",
            on_click=handlers.on_continue_after_correct_click,
            when="is_correct",
        ),
        Group(
            Url(
                Const("Перейти в канал эксперта"),
                Format("{channel_url}"),
                id="go_to_channel",
                when="not_is_correct",
            ),
            Button(
                Const("Попробовать еще раз"),
                id="retry",
                on_click=handlers.on_retry_question_click,
                when="not_is_correct",
            ),
        ),
        getter=getters.get_answer_feedback,
        state=PollSG.answer_feedback,
    ),

    Window(
        Const(templates.MID_POLL_REMINDER_TEXT),
        Button(
            Const("Продолжить"),
            id="continue",
            on_click=handlers.on_continue_poll_click,
        ),
        state=PollSG.mid_poll_reminder,
    ),
    Window(
        Format(templates.POLL_COMPLETED_TEXT),
        Group(
            Button(
                Const("Увеличить шансы"),
                id="increase_chances",
                on_click=handlers.on_increase_chances_click,
            ),
            Button(
                Const("Оставить как есть"),
                id="leave_as_is",
                on_click=handlers.on_leave_as_is_click,
            ),
        ),
        getter=getters.get_poll_completed_data,
        state=PollSG.poll_completed,
    ),
    Window(
        Format(templates.REFERRAL_SCREEN_TEXT),
        Group(
            SwitchInlineQuery(
                Const("Поделиться ботом"),
                id="share_bot",
                switch_inline_query=Format("Пройди опрос и выиграй поездку в Дубай: https://t.me/d1capital_quizbot?start={ref_code}"),
            ),
            Button(
                Const("Мои шансы"),
                id="my_chances",
                on_click=handlers.on_my_chances_click,
            ),
        ),
        getter=getters.get_referral_data,
        state=PollSG.referral_screen,
    ),

    # Мои шансы
    Window(
        Format(templates.MY_CHANCES_TEXT),
        Group(
            Button(
                Const("Пригласить еще"),
                id="invite_more",
                on_click=handlers.on_invite_more_click,
            ),
            SwitchTo(
                Const("Назад"),
                id="back",
                state=PollSG.referral_screen,
            ),
        ),
        getter=getters.get_my_chances_data,
        state=PollSG.my_chances,
    ),

    # Уже прошел опрос
    Window(
        Format(templates.ALREADY_COMPLETED_TEXT),
        Group(
            SwitchInlineQuery(
                Const("Поделиться ботом"),
                id="share_bot",
                switch_inline_query=Format("Пройди опрос и выиграй поездку в Дубай: https://t.me/d1capital_quizbot?start={ref_code}"),
            ),
            Button(
                Const("Мои шансы"),
                id="my_chances",
                on_click=handlers.on_my_chances_click,
            ),
        ),
        getter=getters.get_already_completed_data,
        state=PollSG.already_completed,
    ),
)
