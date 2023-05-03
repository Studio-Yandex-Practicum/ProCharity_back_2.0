from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import User
from src.core.db.repository.base import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Возвращает пользователя (или None) по telegram_id."""
        user = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        return user.scalars().first()

    async def restore_existing_user(self, user: User, username: str) -> User:
        """Обновляет данные пользователя, который уже был в базе.

        Если ранее существовавший юзер делает /start в боте, то проверяется/обновляется username
        и сбрасывается флаг "banned" - признак, что бот у него был заблокирован.
        """
        if user.username != username or user.banned:
            user.username, user.banned = username, False
            await self.update(user.id, user)
        return user
