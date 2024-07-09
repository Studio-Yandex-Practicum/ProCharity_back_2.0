from src.core.db.models import ExternalSiteUser
from src.core.db.repository import ExternalSiteUserRepository, UserRepository


class ExternalSiteUserService:
    """Сервис бота для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository, user_repository: UserRepository):
        self._repository = site_user_repository
        self._user_repository = user_repository

    async def get_by_id_hash(self, id_hash: str, is_archived: bool | None = False) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id_hash."""
        return await self._repository.get_by_id_hash(id_hash, is_archived)

    async def get_by_id(self, id: int) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id."""
        return await self._repository.get_or_none(id)

    async def get_by_telegram_id(self, telegram_id: int) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по telegram_id."""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if user and user.external_id is not None:
            return await self._repository.get_or_none(user.external_id)
