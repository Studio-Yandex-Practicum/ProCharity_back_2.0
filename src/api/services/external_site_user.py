from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import (
    ExternalSiteFundPartialUpdate,
    ExternalSiteFundRequest,
    ExternalSiteVolunteerPartialUpdate,
    ExternalSiteVolunteerRequest,
)
from src.core.db.models import ExternalSiteUser
from src.core.db.repository import ExternalSiteUserRepository, UserRepository
from src.core.enums import UserRoles
from src.core.exceptions import BadRequestException


class ExternalSiteUserService:
    """Сервис для работы с моделью ExternalSiteUser."""

    def __init__(
        self,
        user_repository: UserRepository,
        site_user_repository: ExternalSiteUserRepository,
        session: AsyncSession,
    ) -> None:
        self._user_repository: UserRepository = user_repository
        self._site_user_repository: ExternalSiteUserRepository = site_user_repository
        self._session: AsyncSession = session

    async def register(self, site_user_schema: ExternalSiteVolunteerRequest | ExternalSiteFundRequest) -> None:
        """Создаёт в БД нового пользователя сайта или обновляет данные существующего."""
        site_user = await self._site_user_repository.get_by_id_hash(site_user_schema.id_hash, None)
        if site_user:
            if site_user.is_archived:
                raise BadRequestException("Пользователь удален. Обновление невозможно.")

            site_user = await self._site_user_repository.update(site_user.id, site_user_schema.to_orm())

        else:
            site_user = await self._site_user_repository.create(site_user_schema.to_orm())

        user = await self._user_repository.get_by_external_id(site_user.id)
        if user:
            user.email = site_user.email
            user.first_name = site_user.first_name
            user.last_name = site_user.last_name
            user.role = site_user.role

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
            for attr, value in data_for_update.items():
                setattr(user, attr, value)

            await self._user_repository.update(user.id, user)

            if site_user.role == UserRoles.VOLUNTEER:
                await self._user_repository.set_categories_to_user(user.id, site_user.specializations)

    async def archive(self, external_id: int) -> None:
        """Архивирует пользователя сайта и удаляет его связь с ботом."""
        await self._site_user_repository.archive(external_id)
