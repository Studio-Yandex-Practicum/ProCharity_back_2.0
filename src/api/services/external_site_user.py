from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import ExternalSiteUserRequest
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

    async def register(self, site_user_schema: ExternalSiteUserRequest) -> None:
        site_user = await self._site_user_repository.get_by_id_hash(site_user_schema.id_hash)
        user = await self._user_repository.get_by_user_id(site_user_schema.user_id)
        if site_user:
            await self._site_user_repository.update(site_user.id, site_user_schema.to_orm())
        else:
            await self._site_user_repository.create(site_user_schema.to_orm())
        if user:
            await self._user_repository.set_categories_to_user(
                site_user_schema.user_id, site_user_schema.specializations
            )
