from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import ContentService
from src.core.db.models import User
from src.core.db.repository import UserRepository


class UserService(ContentService):
    """Сервис для работы с моделью User."""

    def __init__(
        self,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        self._user_repository: UserRepository = user_repository
        self._session: AsyncSession = session

    async def get_by_user_id(self, user_id: int) -> User | None:
        return await self._user_repository.get_by_user_id(user_id)

    async def get_users_by_page(self, page: int, limit: int) -> list[User]:
        offset = (page - 1) * limit
        return await self._user_repository.get_users_by_page(limit, offset)
