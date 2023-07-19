from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.db.db import get_session
from src.core.db.models import Category, Task, User
from src.core.db.repository.base import ContentRepository


class TaskRepository(ContentRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Task)

    async def get_tasks_for_user(self, user_id: int) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        tasks = await self._session.execute(select(Task).join(Category).where(Category.users.any(id=user_id)))
        return tasks.scalars().all()

    async def get_tasks_for_user_in_telegram(self, user_telegram_id: int, limit: int) -> list[Task]:
        """Получить список задач в телеграм боте из категорий на которые подписан пользователь."""
        user_id = await self._session.scalar((select(User.id).where(User.telegram_id == user_telegram_id)))
        return await self._session.scalars(
            select(Task)
            .join(Category)
            .options(joinedload(Task.category))
            .where(Category.users.any(id=user_id))
            .limit(limit))
