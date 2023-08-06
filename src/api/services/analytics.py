from fastapi import Depends

from src.core.db.repository import UserRepository


class AnalyticsService:
    """Сервис для работы с моделью Analytics."""

    def __init__(self, user_repository: UserRepository = Depends()) -> None:
        self._user_repository: UserRepository = user_repository

    async def get_user_number(self) -> None:
        return await self._user_repository.count_all()
