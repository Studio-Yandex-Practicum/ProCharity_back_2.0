from sqlalchemy.ext.asyncio import AsyncSession

from src.api.pagination import paginate
from src.api.utils import format_user
from src.core.db.models import User
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
        users = await self._user_repository.get_objects_by_page(User, page, limit)
        count_users = await self._user_repository.count_all()

        result = []
        for user in users:
            result.append(format_user(user))

        return paginate(result, count_users, page, limit, settings.users_url)
