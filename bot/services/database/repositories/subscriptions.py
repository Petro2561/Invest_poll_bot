from typing import Optional, cast

from sqlalchemy import desc, select

from bot.services.database.models.user import BondSubscription

from ..models import BondSubscription
from .base import BaseRepository
from sqlalchemy.sql import or_, and_


class BondSubscriptionsRepository(BaseRepository):
    async def get(self, id: int) -> Optional[BondSubscription]:
        return cast(
            Optional[BondSubscription],
            await self._session.scalar(select(BondSubscription).where(BondSubscription.id == id)),
        )

    async def get_users_subscriptions(self, user_id: int) -> list[BondSubscription]:
        result = await self._session.execute(
            select(BondSubscription)
            .where(and_(
                BondSubscription.user_id == user_id,
                BondSubscription.is_deleted == False
            ))
            .order_by(desc(BondSubscription.id))
        )
        return list(result.scalars().all())
