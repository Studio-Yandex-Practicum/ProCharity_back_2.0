from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import ExternalSiteFundRequest, ExternalSiteVolunteerRequest
from src.core.db.repository import ExternalSiteUserRepository, UserRepository


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

    async def archive(self, external_id: int) -> None:
        await self._site_user_repository.archive(external_id)
