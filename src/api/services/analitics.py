from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import Analytic
from src.core.db import get_session
from src.core.db.models import User
from src.core.db.repository.base import AbstractRepository


class AnalyticsService:
    """Сервис для работы с моделью Analitics."""

    # def __init__(self, repository: AbstractRepository = Depends()) -> None:
    #     self._repository: AbstractRepository = repository
        # self._session: AsyncSession = session

    async def get_user_number(self) -> None:
        analytic = Analytic
        print("AbstractRepository", type(self._repository.count_all(User)), self._repository.count_all(User))
        analytic.number_users = int(self._repository.count_all(User))
        return analytic
        # pass
