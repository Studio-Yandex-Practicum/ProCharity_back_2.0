from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.db.db import get_session
from src.core.db.models import Category, Task
from src.core.db.repository.base import ContentRepository


class TaskRepository(ContentRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Task)

    async def get_tasks_for_user(self, user_id: int) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        tasks = await self._session.execute(select(Task).join(Category).where(Category.users.any(id=user_id)))
        return tasks.scalars().all()

    async def get_user_tasks(self, limit: int) -> list[Task]:
        """Получить список задач из категорий."""
        return await self._session.scalars(select(Task).options(joinedload(Task.category)).limit(limit))

    async def get_all_user_tasks(self) -> list[Task]:
        """Получить список задач из категорий."""
        return await self._session.scalars(select(Task).options(joinedload(Task.category)))
