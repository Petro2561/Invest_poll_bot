from aiogram import html
from aiogram.types import User
from aiogram.utils.link import create_tg_link
from sqlalchemy import (
    Float,
    ForeignKey,
    Integer,
    String,
    Enum as SQLAlchemyEnum
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from bot.enums import EventType, ActionType

from .base import Base, Int64, TimestampMixin


class DBUser(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[Int64] = mapped_column(primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=True)
    username: Mapped[str] = mapped_column(unique=False, nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False, nullable=False)
    # Кто пригласил этого пользователя
    referrer_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    # Прошел ли опрос
    has_completed_poll: Mapped[bool] = mapped_column(
        default=False, nullable=False
    )
    # Количество пройденных вопросов
    questions_completed: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
    bond_subscriptions = relationship(
        "BondSubscription", back_populates="user"
    )

    def __str__(self) -> str:
        return self.username or self.name or f"User {self.id}"

    @property
    def url(self) -> str:
        return create_tg_link("user", id=self.id)

    @property
    def mention(self) -> str:
        return html.link(value=self.name, link=self.url)

    @classmethod
    def from_aiogram(cls, user: User):
        return cls(
            id=user.id,
            name=user.full_name,
            username=user.username
        )


class BondSubscription(Base, TimestampMixin):
    __tablename__ = "bond_subscriptions"

    id = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    uid: Mapped[str] = mapped_column(String, nullable=False)
    ticker: Mapped[str] = mapped_column(String, nullable=True)
    event_type: Mapped[EventType] = mapped_column(
        SQLAlchemyEnum(EventType), nullable=False
    )
    action_type: Mapped[ActionType] = mapped_column(
        SQLAlchemyEnum(ActionType), nullable=True
    )
    user_id: Mapped[Int64] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    lots: Mapped[float] = mapped_column(
        Float, nullable=False
    )
    price: Mapped[float] = mapped_column(
        Float, nullable=True
    )
    price_range: Mapped[float] = mapped_column(
        Float, nullable=True
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=True)
    nominal: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    user = relationship("DBUser", back_populates="bond_subscriptions")
