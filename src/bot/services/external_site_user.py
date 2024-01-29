from src.core.db.models import ExternalSiteUser
from src.core.db.repository.external_site_user import ExternalSiteUserRepository


class ExternalSiteUserService:
    """Сервис бота для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository):
        self._site_user_repository = site_user_repository

    async def get_ext_user_by_args(self, args) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по арументам."""
        if args:
            id_hash = args[0]
            return await self._site_user_repository.get_by_id_hash(id_hash)
        return None

    async def update_user_id_in_external_site_user(self, ext_user_id, user_id):
        await self._site_user_repository.update_user_id_in_external_site_user(ext_user_id, user_id)
