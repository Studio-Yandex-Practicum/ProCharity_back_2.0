from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    ExternalSiteFundPartialUpdate,
    ExternalSiteFundRequest,
    ExternalSiteVolunteerPartialUpdate,
    ExternalSiteVolunteerRequest,
)
from src.core.db.models import ExternalSiteUser
from src.core.db.repository import ExternalSiteUserRepository, TaskRepository, UserRepository
from src.core.enums import UserResponseAction, UserRoles
from src.core.exceptions import BadRequestException


class ExternalSiteUserService:
    """Сервис для работы с моделью ExternalSiteUser."""

    def __init__(
        self,
        user_repository: UserRepository,
        site_user_repository: ExternalSiteUserRepository,
        task_repository: TaskRepository,
        session: AsyncSession,
    ) -> None:
        self._user_repository: UserRepository = user_repository
        self._site_user_repository: ExternalSiteUserRepository = site_user_repository
        self._task_repository: TaskRepository = task_repository
        self._session: AsyncSession = session

    async def register(self, site_user_schema: ExternalSiteVolunteerRequest | ExternalSiteFundRequest) -> None:
        """Создаёт в БД нового пользователя сайта или обновляет данные существующего."""
        site_user_role = site_user_schema.get_role()
        data_for_update = site_user_schema.model_dump(exclude_none=True)
        data_for_update["role"] = site_user_role
        if site_user_role == UserRoles.FUND:
            data_for_update["specializations"] = None

        site_user = await self._site_user_repository.get_by_external_id_or_none(site_user_schema.external_id, None)

        if site_user:
            if site_user.is_archived:
                raise BadRequestException("Пользователь удален. Обновление невозможно.")

            if site_user.id_hash not in (None, site_user_schema.id_hash):
                raise BadRequestException("Изменение id_hash у существующего пользователя запрещено.")

            if site_user.id_hash is None:
                await self._error_if_exists_by_id_hash(site_user_schema.id_hash)

            site_user = await self._site_user_repository.update(site_user.id, ExternalSiteUser(**data_for_update))

        else:
            await self._error_if_exists_by_id_hash(site_user_schema.id_hash)
            site_user = await self._site_user_repository.create(ExternalSiteUser(**data_for_update))

        user = await self._user_repository.get_by_external_id(site_user.id)
        if user:
            user.email = site_user.email
            user.first_name = site_user.first_name
            user.last_name = site_user.last_name
            user.role = site_user.role
            if site_user.has_mailing_new_tasks:
                user.has_mailing = site_user.has_mailing_new_tasks

            await self._user_repository.update(user.id, user)
            await self._user_repository.set_categories_to_user(user.id, site_user.specializations)

    async def partial_update(
        self, external_id: int, site_user_schema: ExternalSiteVolunteerPartialUpdate | ExternalSiteFundPartialUpdate
    ) -> None:
        """Обновляет данные/часть данных существующего пользователя сайта."""
        data_for_update = site_user_schema.model_dump(exclude_none=True)
        site_user = await self._site_user_repository.get_by_external_id(external_id, None)
        if site_user and site_user.is_archived:
            raise BadRequestException("Пользователь удален. Обновление невозможно.")

        await self._site_user_repository.update(site_user.id, ExternalSiteUser(**data_for_update))

        user = await self._user_repository.get_by_external_id(site_user.id)
        if user:
            if site_user.has_mailing_new_tasks:
                user.has_mailing = site_user.has_mailing_new_tasks
            for attr, value in data_for_update.items():
                setattr(user, attr, value)

            await self._user_repository.update(user.id, user)

            if site_user.role == UserRoles.VOLUNTEER:
                await self._user_repository.set_categories_to_user(user.id, site_user.specializations)

    async def archive(self, external_id: int) -> None:
        """Архивирует пользователя сайта и удаляет его связь с ботом."""
        await self._site_user_repository.archive(external_id)

    async def change_user_response_to_task(self, site_user_id: int, task_id: int, action: UserResponseAction) -> None:
        """Изменяет отклик заданного пользователя на заданную задачу."""
        site_user = await self._site_user_repository.get_by_external_id(site_user_id)
        task = await self._task_repository.get(task_id)
        if action is UserResponseAction.RESPOND:
            await self._site_user_repository.create_user_response_to_task(site_user, task)
        else:
            await self._site_user_repository.delete_user_response_to_task(site_user, task)

    async def _error_if_exists_by_id_hash(self, id_hash: str) -> None:
        """Возбуждает BadRequestException, если в БД есть запись с указанным id_hash (архивная или нет)."""
        site_user = await self._site_user_repository.get_by_id_hash(id_hash, is_archived=None)
        if site_user is not None:
            raise BadRequestException(
                "Указанный id_hash не может быть установлен."
                if site_user.is_archived
                else "Пользователь с таким id_hash уже существует."
            )
