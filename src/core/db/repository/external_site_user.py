from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import ExternalSiteUser
from src.core.db.repository.base import AbstractRepository


class ExternalSiteUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью ExternalSiteUser."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, ExternalSiteUser)

    async def get_by_external_id(self, external_id: int) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по external_id."""
        return await self._session.scalar(
            select(ExternalSiteUser).where(ExternalSiteUser.external_id == external_id)  # noqa
        )
