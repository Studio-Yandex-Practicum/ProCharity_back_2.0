from src.core.db.models import ExternalSiteUser, Task
from src.core.db.repository import ExternalSiteUserRepository, UserRepository


class ExternalSiteUserService:
    """Сервис бота для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository, user_repository: UserRepository):
        self._repository = site_user_repository
        self._user_repository = user_repository

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

    async def get_by_telegram_id(self, telegram_id: int) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по telegram_id."""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if user and user.external_id is not None:
            return await self._repository.get_or_none(user.external_id)

    async def user_responded_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Возвращает True, если в БД имеется отклик заданного пользователя
        на заданную задачу, иначе False.
        """
        return await self._repository.user_responded_to_task(site_user, task)

    async def create_user_response_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Создаёт отклик заданного пользователя на заданную задачу и возвращает True.
        А если такой отклик уже есть в БД, просто возвращает False.
        """
        return await self._repository.create_user_response_to_task(site_user, task)

    async def delete_user_response_to_task(self, site_user: ExternalSiteUser, task: Task) -> bool:
        """Удаляет отклик заданного пользователя на заданную задачу и возвращает True.
        А если такого отклика нет в БД, просто возвращает False.
        """
        return await self._repository.delete_user_response_to_task(site_user, task)
