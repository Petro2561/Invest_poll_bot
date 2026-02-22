from datetime import datetime
from typing import Optional

from sqlalchemy import Integer, ForeignKey, Boolean, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, Int64, TimestampMixin


class Poll(Base, TimestampMixin):
    """Модель опроса с вопросом и 8 вариантами ответов"""
    __tablename__ = "polls"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    question_text: Mapped[str] = mapped_column(
        Text, nullable=False
    )  # Текст вопроса

    # 8 полей для ответов (могут быть пустыми)
    answer_1: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_2: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_3: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_4: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_5: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_6: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_7: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    answer_8: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Номер правильного ответа (1-8)
    correct_answer: Mapped[int] = mapped_column(Integer, nullable=False)

    # Подсказка при неправильном ответе (опционально)
    hint: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class Referral(Base, TimestampMixin):
    """Модель реферальной системы"""
    __tablename__ = "referrals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    referrer_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )  # Кто пригласил
    referred_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )  # Кого пригласили
    is_completed: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )  # Прошел ли опрос до конца
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
