from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from src.core.db.models import UnsubscribeReason
from src.core.db.repository.base import AbstractRepository


class UnsubscribeReasonRepository(AbstractRepository):
    """Репозиторий для работы с моделью UnsubscribeReason."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UnsubscribeReason)

    async def get_by_user(self, user):
        return await self._session.scalar(select(UnsubscribeReason).where(UnsubscribeReason.user == user))

    async def get_reason_cancelling_statistics(self) -> list[tuple[str, int]]:
        query = select(
            UnsubscribeReason.unsubscribe_reason.label("reason"),
            func.count(UnsubscribeReason.unsubscribe_reason).label("count"),
        ).group_by(UnsubscribeReason.unsubscribe_reason)
        reasons = await self._session.execute(query)
        return reasons.all()

