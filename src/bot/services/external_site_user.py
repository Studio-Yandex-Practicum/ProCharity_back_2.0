from src.core.db.models import ExternalSiteUser
from src.core.db.repository.external_site_user import ExternalSiteUserRepository


class ExternalSiteUserService:
    """Сервис бота для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository):
        self._repository = site_user_repository

    async def get_or_create_by_args(self, *args) -> tuple[ExternalSiteUser | None, bool]:
        """Возвращает пользователя (или None) по арументам."""
        if not args:
            return (False, None)
        return await self._repository.get_or_create_by_id_hash(args[0])
