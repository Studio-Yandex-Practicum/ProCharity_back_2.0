from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import ExternalSiteUserRequest
from src.api.services.base import ContentService
from src.core.db import get_session
from src.core.db.models import ExternalSiteUser
from src.core.db.repository.external_site_user import ExternalSiteUserRepository


class ExternalSiteUserService(ContentService):
    """Сервис для работы с моделью ExternalSiteUser."""

    def __init__(
        self, site_user_repository: ExternalSiteUserRepository = Depends(), session: AsyncSession = Depends(get_session)
    ) -> None:
        super().__init__(site_user_repository, session)

    async def register(self, site_user_schema: ExternalSiteUserRequest) -> None:
        site_user = await self._repository.get_by_external_id(site_user_schema.external_id)
        if site_user:
            await self._repository.update(None, ExternalSiteUser(**site_user_schema.dict()))
        else:
            await self._repository.create(ExternalSiteUser(**site_user_schema.dict()))
