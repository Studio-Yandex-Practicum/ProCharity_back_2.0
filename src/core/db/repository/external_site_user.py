from sqlalchemy import false, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import ExternalSiteUser
from src.core.db.repository.base import AbstractRepository
from src.core.exceptions import NotFoundException


class ExternalSiteUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью ExternalSiteUser."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, ExternalSiteUser)

    async def get_by_id_hash(self, id_hash: str, with_archived=False) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id_hash."""
        statement = select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash)
        if not with_archived:
            statement = statement.where(self._model.is_archived == false())
        return await self._session.scalar(statement)

    async def get_or_create_by_id_hash(self, id_hash: str) -> tuple[ExternalSiteUser, bool]:
        """Возвращает или создает пользователя по id_hash."""
        instance = await self._session.scalar(select(ExternalSiteUser).where(ExternalSiteUser.id_hash == id_hash))
        if instance is not None:
            return (instance, False)
        return await self.create(ExternalSiteUser(id_hash=id_hash)), True

    async def get_by_external_id_or_none(self, external_id: int, with_archived=False) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по external_id."""
        statement = select(self._model).where(self._model.external_id == external_id)
        if not with_archived:
            statement = statement.where(self._model.is_archived == false())
        return await self._session.scalar(statement)

    async def get_by_external_id(self, external_id: int, with_archived=False) -> ExternalSiteUser:
        """Возвращает пользователя по external_id, а в случае его отсутствия
        возбуждает исключение NotFoundException.
        """
        instance = await self.get_by_external_id_or_none(external_id, with_archived)
        if instance is None:
            raise NotFoundException(object_name=self._model.__name__, external_id=external_id)
        return instance

    async def archive(self, external_id: int) -> None:
        instance = await self.get_by_external_id(external_id)
        instance.is_archived = True
        instance.user = None
        await self.update(instance.id, instance)
