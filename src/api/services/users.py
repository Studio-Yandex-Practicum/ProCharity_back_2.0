from sqlalchemy.ext.asyncio import AsyncSession

from src.api.pagination import paginate
from src.api.utils import format_user
from src.core.db.repository import UserRepository
from src.core.services import BaseUserService
from src.settings import settings


class UserService(BaseUserService):
    """Сервис для работы с моделью User."""

    def __init__(
        self,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        self._user_repository: UserRepository = user_repository

    async def get_users_by_page(self, page: int, limit: int) -> dict:
        return await paginate(self._user_repository, page, limit, settings.users_url, format_user)
