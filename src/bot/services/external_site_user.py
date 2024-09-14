from src.core.db.models import ExternalSiteUser, Task
from src.core.db.repository import ExternalSiteUserRepository, UserRepository


class ExternalSiteUserService:
    """Сервис бота для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository, user_repository: UserRepository):
        self._repository = site_user_repository
        self._user_repository = user_repository

    async def get_by_id_hash(self, id_hash: str, is_archived: bool | None = False) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id_hash."""
        return await self._repository.get_by_id_hash(id_hash, is_archived)

    async def get_by_id(self, id: int, is_archived: bool | None = False) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по id."""
        return await self._repository.get_or_none(id, is_archived=is_archived)

    async def get_by_telegram_id(self, telegram_id: int, is_archived: bool | None = False) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по telegram_id."""
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        if user and user.external_id is not None:
            return await self._repository.get_or_none(user.external_id, is_archived=is_archived)

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

    async def set_mailing_new_tasks_status(self, site_user: ExternalSiteUser, status: bool) -> ExternalSiteUser:
        """Устанавливает новое значение поля has_mailing_new_tasks у заданного пользователя."""
        site_user.has_mailing_new_tasks = status
        return await self._repository.update(site_user.id, site_user)

    async def set_specializations(self, site_user: ExternalSiteUser, specializations: list[int]) -> ExternalSiteUser:
        """Устанавливает новое значение поля specializations у заданного пользователя."""
        site_user.specializations = specializations
        return await self._repository.update(site_user.id, site_user)
