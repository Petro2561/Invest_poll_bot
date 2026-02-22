from fastapi import FastAPI
from sqladmin import Admin, ModelView
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import selectinload
from markupsafe import Markup
from starlette.middleware.sessions import SessionMiddleware

from bot.config import load_config
from bot.services.database.models.user import DBUser, BondSubscription
from bot.services.database.models.poll import Poll
# Импортируем все модели, чтобы они были в Base.metadata
from bot.services.database.models import Base
import settings
from .auth import AdminAuth

config = load_config()
engine = create_async_engine(url=config.database.url, echo=True)

app = FastAPI()

app.add_middleware(SessionMiddleware, secret_key=config.admin_config.secret_key)
authentication_backend = AdminAuth(secret_key=config.admin_config.secret_key)

admin = Admin(
    app=app,
    engine=engine,
    authentication_backend=authentication_backend,
    templates_dir="bot/admin/templates",
)


@app.get("/")
async def root():
    """Тестовый маршрут для проверки работы приложения"""
    return {"message": "Admin panel is running", "admin_url": "/admin"}


class UserAdmin(ModelView, model=DBUser):
    column_list = [
        DBUser.id,
        DBUser.name,
        DBUser.username,
        DBUser.created_at,
        DBUser.is_admin,
        DBUser.questions_completed,
    ]
    column_labels = {
        DBUser.is_admin: "Админ",
        DBUser.questions_completed: "Количество пройденных вопросов",
    }
    name_plural = "Пользователи"
    column_default_sort = "created_at"
    column_searchable_list = [DBUser.username]


class PollAdmin(ModelView, model=Poll):
    column_list = [
        Poll.id,
        Poll.question_text,
        Poll.answer_1,
        Poll.answer_2,
        Poll.answer_3,
        Poll.answer_4,
        Poll.answer_5,
        Poll.answer_6,
        Poll.answer_7,
        Poll.answer_8,
        Poll.correct_answer,
        Poll.hint,
        Poll.created_at,
    ]
    column_labels = {
        Poll.question_text: "Вопрос",
        Poll.answer_1: "Ответ 1",
        Poll.answer_2: "Ответ 2",
        Poll.answer_3: "Ответ 3",
        Poll.answer_4: "Ответ 4",
        Poll.answer_5: "Ответ 5",
        Poll.answer_6: "Ответ 6",
        Poll.answer_7: "Ответ 7",
        Poll.answer_8: "Ответ 8",
        Poll.correct_answer: "Правильный ответ",
        Poll.hint: "Подсказка",
    }
    name_plural = "Опросы"
    name = "Опрос"
    column_default_sort = "id"
    column_searchable_list = [Poll.question_text]
    
    # Форматирование для отображения
    column_formatters = {
        Poll.question_text: lambda m, _: (
            f"{m.question_text[:100]}..." if len(m.question_text) > 100 else m.question_text
        ),
        Poll.correct_answer: lambda m, _: f"Ответ {m.correct_answer}",
    }



admin.add_view(UserAdmin)
admin.add_view(PollAdmin)
