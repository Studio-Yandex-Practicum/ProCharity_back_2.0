from src.core.db.models import ExternalSiteUser
from src.core.db.repository.external_site_user import ExternalSiteUserRepository


class ExternalSiteUserService:
    """Сервис бота для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository):
        self._repository = site_user_repository

    async def get_or_create(self, id_hash: str | None) -> tuple[ExternalSiteUser | None, bool]:
        """Возвращает или создает пользователя (или None) по id_hash."""
        if id_hash is None:
            return (None, False)
        return await self._repository.get_or_create_by_id_hash(id_hash)

    async def get_by_id_hash(self, id_hash: str) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id_hash."""
        return await self._repository.get_by_id_hash(id_hash)

    async def get_by_id(self, id: int) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id."""
        return await self._repository.get_or_none(id)
