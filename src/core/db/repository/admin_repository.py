from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import AdminUser
from src.core.db.repository.base import AbstractRepository


class AdminUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью AdminUser."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AdminUser)

    async def get_by_email(self, email: str) -> AdminUser | None:
        """Возвращает пользователя (или None) по email."""
        return await self._session.scalar(select(AdminUser).where(AdminUser.email == email))
