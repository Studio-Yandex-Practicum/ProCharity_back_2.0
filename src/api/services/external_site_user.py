from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import ExternalSiteUserRequest
from src.core.db.repository.external_site_user import ExternalSiteUserRepository


class ExternalSiteUserService:
    """Сервис для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository, session: AsyncSession) -> None:
        self._repository = site_user_repository
        self._session = session

    async def register(self, site_user_schema: ExternalSiteUserRequest) -> None:
        site_user = await self._repository.get_by_id_hash(site_user_schema.id_hash)
        if site_user:
            await self._repository.update(site_user.id, site_user_schema.to_orm())
        else:
            await self._repository.create(site_user_schema.to_orm())
