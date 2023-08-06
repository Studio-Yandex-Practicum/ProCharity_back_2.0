from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import Analytic
from src.core.db import get_session
from src.core.db.models import User
from src.core.db.repository import UserRepository


class AnalyticsService:
    """Сервис для работы с моделью Analitics."""

    def __init__(self, user_repository: UserRepository = Depends()) -> None:
        self._user_repository: UserRepository = user_repository
        # self._session: AsyncSession = session

    async def get_user_number(self) -> None:
        analytic = Analytic()
        analytic.number_users = int(self._user_repository.count_all(User))
        return analytic
