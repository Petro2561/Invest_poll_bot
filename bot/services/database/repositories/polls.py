from typing import Optional, List, cast
from datetime import datetime

from sqlalchemy import select, and_, func

from ..models import Poll, Referral
from .base import BaseRepository


class PollRepository(BaseRepository):
    """Репозиторий для работы с опросами"""

    async def get_by_id(self, poll_id: int) -> Optional[Poll]:
        """Получить опрос по ID"""
        return cast(
            Optional[Poll],
            await self._session.scalar(
                select(Poll).where(Poll.id == poll_id)
            )
        )

    async def get_all(self) -> List[Poll]:
        """Получить все опросы"""
        result = await self._session.execute(
            select(Poll).order_by(Poll.id)
        )
        return list(result.scalars().all())

    async def get_total_count(self) -> int:
        """Получить общее количество опросов"""
        result = await self._session.scalar(
            select(func.count(Poll.id))
        )
        return result or 0

    def get_answer_text(self, poll: Poll, answer_number: int) -> Optional[str]:
        """Получить текст ответа по номеру (1-8)"""
        answer_map = {
            1: poll.answer_1,
            2: poll.answer_2,
            3: poll.answer_3,
            4: poll.answer_4,
            5: poll.answer_5,
            6: poll.answer_6,
            7: poll.answer_7,
            8: poll.answer_8,
        }
        return answer_map.get(answer_number)

    def get_all_answers(self, poll: Poll) -> List[tuple[int, Optional[str]]]:
        """Получить все ответы опроса в виде списка (номер, текст)"""
        answers = []
        for i in range(1, 9):
            text = self.get_answer_text(poll, i)
            if text:  # Добавляем только непустые ответы
                answers.append((i, text))
        return answers


class ReferralsRepository(BaseRepository):
    """Репозиторий для работы с реферальной системой"""

    async def get_by_referred_id(self, referred_id: int) -> Optional[Referral]:
        return cast(
            Optional[Referral],
            await self._session.scalar(
                select(Referral)
                .where(Referral.referred_id == referred_id)
            )
        )

    async def get_referrer_referrals(
        self, referrer_id: int, only_completed: bool = True
    ) -> List[Referral]:
        query = select(Referral).where(Referral.referrer_id == referrer_id)
        if only_completed:
            query = query.where(Referral.is_completed.is_(True))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def create_referral(
        self, referrer_id: int, referred_id: int
    ) -> Referral:
        referral = Referral(
            referrer_id=referrer_id,
            referred_id=referred_id,
            is_completed=False
        )
        self._session.add(referral)
        await self._session.flush()
        return referral

    async def mark_completed(self, referred_id: int) -> Optional[Referral]:
        referral = await self.get_by_referred_id(referred_id)
        if referral and not referral.is_completed:
            referral.is_completed = True
            referral.completed_at = datetime.now()
            await self._session.flush()
        return referral

    async def count_completed_referrals(self, referrer_id: int) -> int:
        result = await self._session.scalar(
            select(func.count(Referral.id))
            .where(
                and_(
                    Referral.referrer_id == referrer_id,
                    Referral.is_completed.is_(True)
                )
            )
        )
        return result or 0
