from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import UnsubscribeReason
from src.core.db.repository.base import AbstractRepository


class UnsubscribeReasonRepository(AbstractRepository):
    """Репозиторий для работы с моделью UnsubscribeReason."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, UnsubscribeReason)

    async def get_by_user(self, user):
        db_obj = await self._session.execute(select(self._model).where(self._model.user == user))
        return db_obj.scalars().first()