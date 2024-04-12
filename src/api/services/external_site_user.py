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

        if site_user:
            await self._site_user_repository.update(site_user.id, site_user_schema.to_orm())
        else:
            await self._site_user_repository.create(site_user_schema.to_orm())

        if site_user.user:
            site_user.user.email = site_user_schema.email
            site_user.user.first_name = site_user_schema.first_name
            site_user.user.last_name = site_user_schema.last_name

            if site_user.role == UserRoles.VOLUNTEER:
                site_user.user.role = UserRoles.VOLUNTEER
                await self._user_repository.set_categories_to_user(site_user.user.id, site_user_schema.specializations)
            else:
                site_user.user.role = UserRoles.FUND
                await self._user_repository.delete_all_categorys_from_user(site_user.user)

                site_user.specializations = None

            await self._user_repository.update(site_user.user.id, site_user.user)
