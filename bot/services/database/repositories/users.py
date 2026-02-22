from typing import Optional, cast

from sqlalchemy import select

from ..models import DBUser
from .base import BaseRepository
from sqlalchemy.sql import or_, and_
from sqlalchemy.orm import joinedload




class UsersRepository(BaseRepository):
    async def get(self, user_id: int) -> Optional[DBUser]:
        return cast(
            Optional[DBUser],
            await self._session.scalar(
                select(DBUser)
                .options(joinedload(DBUser.bond_subscriptions))  # <-- важно
                .where(DBUser.id == user_id)
            ),
        )
    
    async def get_by_email(self, email: str) -> Optional[DBUser]:
        return cast(
            Optional[DBUser],
            await self._session.scalar(select(DBUser).where(DBUser.email == email)),
        )
    

    async def get_all_users(self) -> list[DBUser]:
        result = await self._session.execute(select(DBUser))
        return list(result.scalars().all())
    
    
    async def get_admins(self) -> list[DBUser]:
        result = await self._session.execute(
            select(DBUser).where(
                (DBUser.is_admin == True)
            )
        )
        return list(result.scalars().all())
