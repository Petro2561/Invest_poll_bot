from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from .base import BaseRepository
from .users import UsersRepository
from .polls import PollRepository, ReferralsRepository


class Repository(BaseRepository):

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session=session)
        self.users = UsersRepository(session=session)
        self.polls = PollRepository(session=session)
        self.referrals = ReferralsRepository(session=session)
