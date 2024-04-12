from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import ExternalSiteFundRequest, ExternalSiteVolunteerRequest
from src.core.db.repository import ExternalSiteUserRepository, UserRepository
from src.core.enums import UserRoles


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
        site_user = await self._site_user_repository.get_by_id_hash(site_user_schema.id_hash)
        user = site_user.user

        if site_user:
            await self._site_user_repository.update(site_user.id, site_user_schema.to_orm())
        else:
            await self._site_user_repository.create(site_user_schema.to_orm())

        if user:
            user.email = site_user.email
            user.first_name = site_user.first_name
            user.last_name = site_user.last_name
            user.role = site_user.role

            if site_user.role == UserRoles.VOLUNTEER:
                await self._user_repository.set_categories_to_user(user.id, site_user_schema.specializations)
            else:
                await self._user_repository.delete_all_categories_from_user(user)

            await self._user_repository.update(user.id, user)
