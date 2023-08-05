from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.core.db.repository.base import AbstractRepository
from src.api.schemas import Analytic
from src.core.db.models import User


class AnalyticsService:
    """Сервис для работы с моделью Analitics."""

    def __init__(self, repository: AbstractRepository) -> None:
        super().__init__(repository, session)

    async def get_analytic(self):
        analytic = Analytic
        analytic.new_user_number = repository.count_all(User)
        return analytic
