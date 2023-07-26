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

    async def get_tasks_for_user(self, user_id: int, limit: int, offset: int) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        tasks = await self._session.execute(
            select(Task).join(Category).where(Category.users.any(id=user_id)).limit(limit).offset(offset)
        )
        return tasks.scalars().all()

    async def get_all_user_tasks(self) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        return await self._session.scalars(select(Task).options(joinedload(Task.category)))

    async def get_tasks_limit_for_user(self, limit: int, offset: int) -> list[Task]:
        """Получить limit-выборку из списка всех задач пользователя."""
        return await self._session.scalars(select(Task).options(joinedload(Task.category)).limit(limit).offset(offset))

    async def get_user_tasks_count(self) -> int:
        """Получить общее количество задач для пользователя."""
        tasks = await self._session.scalars(select(Task).options(joinedload(Task.category)))
        return len(tasks.all())
    
    async def get_user_task_id(self, task_id) -> list[Task]:
        """Получить задачу по id из категорий на которые подписан пользователь."""
        task = await self._session.execute(select(Task).options(joinedload(Task.category)).where(Task.id == task_id))
        return task.scalars().first()
