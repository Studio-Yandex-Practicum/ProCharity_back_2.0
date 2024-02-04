# В файле service/external_site_user.py

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import ExternalSiteUserRequest
from src.core.db.repository.external_site_user import ExternalSiteUserRepository


class ExternalSiteUserService:
    """Сервис для работы с моделью ExternalSiteUser."""

    def __init__(self, site_user_repository: ExternalSiteUserRepository, session: AsyncSession) -> None:
        self._repository: ExternalSiteUserRepository = site_user_repository
        self._session: AsyncSession = session

    async def external_user_registration(self, site_user: ExternalSiteUserRequest) -> None:
        existing_user = None

        if site_user.id:
            existing_user = await self._repository.get_by_id(site_user.id)

        if existing_user:
            await self.update(site_user)
        else:
            if site_user.id:
                await self.register(site_user)
            elif site_user.hash_id:
                existing_hash_user = await self._repository.get_by_id_hash(site_user.hash_id)
                if existing_hash_user:
                    await self.update(site_user)
                else:
                    await self.register(site_user)
            else:
                raise ValueError("Не указаны обязательные поля 'id' или 'hash_id'.")

    async def register(self, site_user_schema: ExternalSiteUserRequest) -> None:
        await self._repository.create(site_user_schema.to_orm())

    async def update(self, site_user_schema: ExternalSiteUserRequest) -> None:
        site_user = await self._repository.get_by_id(site_user_schema.id)
        if not site_user:
            raise ValueError(f"Пользователь с id {site_user_schema.id} не найден")
        await self._repository.update(site_user.id, site_user_schema.to_orm())
