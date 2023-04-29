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
