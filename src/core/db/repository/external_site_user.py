from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import ExternalSiteUser
from src.core.db.repository.base import AbstractRepository
from src.core.exceptions import NotFoundException


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

    async def get_by_external_id_or_none(self, external_id: int) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по external_id."""
        return await self._session.scalar(select(self._model).where(self._model.external_id == external_id))

    async def get_by_external_id(self, external_id: int) -> ExternalSiteUser:
        """Возвращает пользователя по external_id, а в случае его отсутствия
        возбуждает исключение NotFoundException.
        """
        db_obj = await self.get_by_external_id_or_none(external_id)
        if db_obj is None:
            raise NotFoundException(object_name=self._model.__name__, external_id=external_id)
        return db_obj
