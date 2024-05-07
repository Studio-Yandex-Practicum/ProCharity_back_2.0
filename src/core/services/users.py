from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import User
from src.core.db.repository import UserRepository


class BaseUserService:
    """Базовый класс для UserService."""

    def __init__(
        self,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        self._user_repository: UserRepository = user_repository

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        return await self._user_repository.get_by_telegram_id(telegram_id)
