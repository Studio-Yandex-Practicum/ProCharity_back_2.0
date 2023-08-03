from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import ContentService
from src.core.db import get_session
from src.core.db.repository.user import get_users_number


class AnalyticsService(ContentService):
    """Сервис для работы с моделью Analitics."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(get_users_number, session)

    async def get_users_number(self) -> int:
        return await self._repository.get_users_number
