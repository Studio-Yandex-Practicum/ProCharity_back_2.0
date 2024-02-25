from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import ExternalSiteUser
from src.core.db.repository.base import AbstractRepository


class ExternalSiteUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью ExternalSiteUser."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ExternalSiteUser)

    async def get_by_id_hash(self, id_hash: str) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id_hash."""
        return await self._session.scalar(select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash))

    async def get_or_create_by_id_hash(self, id_hash: str) -> tuple[ExternalSiteUser, bool]:
        """Возвращает или создает пользователя по id_hash."""
        instance = await self._session.scalar(select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash))
        if instance is not None:
            return (instance, False)
        return await self.create(ExternalSiteUser(id_hash=id_hash)), True
