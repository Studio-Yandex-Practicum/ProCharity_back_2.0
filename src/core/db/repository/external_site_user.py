from sqlalchemy import func, select, update
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

    async def update_user_id_in_external_site_user(self, ext_user_id, user_id):
        """
        Обновляет user_id в таблице ExternalSiteUser.

        param ext_user_id: id внешнего пользователя
        param user_id: id пользователя
        """
        query = (
            update(ExternalSiteUser)
            .where(ExternalSiteUser.id == ext_user_id)
            .values({ExternalSiteUser.user_id: user_id, ExternalSiteUser.updated_at: func.current_timestamp()})
        )

        await self._session.execute(query)
        await self._session.commit()
