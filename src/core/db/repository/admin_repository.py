from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import AdminUser
from src.core.db.repository.base import AbstractRepository


class AdminUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью AdminUser."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, AdminUser)
        self._actual_session = get_session()

    async def get_by_email(self, email: str) -> AdminUser | None:
        """Возвращает пользователя (или None) по email."""
        async for session in self._actual_session:
            user = await session.execute(select(AdminUser).where(AdminUser.email == email))
            return user.scalars().first()
