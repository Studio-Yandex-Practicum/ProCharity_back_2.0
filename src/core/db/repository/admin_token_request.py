from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import AdminTokenRequest
from src.core.db.repository.base import AbstractRepository


class AdminTokenRequestRepository(AbstractRepository):
    """Репозиторий для работы с моделью AdminTokenRequest."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AdminTokenRequest)

    async def get_by_token(self, token: str) -> AdminTokenRequest | None:
        """Возвращает пользователя (или None) по invitation token."""
        return await self._session.scalar(select(AdminTokenRequest).where(AdminTokenRequest.token == token))
