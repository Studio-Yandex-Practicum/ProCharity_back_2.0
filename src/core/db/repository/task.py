from fastapi import Depends
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Category, Task
from src.core.db.repository.base import AbstractRepository


class TaskRepository(AbstractRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Task)

    async def archive_all(self) -> None:
        """Добавляет все задачи в архив."""
        await self._session.execute(update(Task).values({"archive": True}))
        await self._session.commit()

    async def get_tasks_in_categories_which_user_subscribe(self, user_id: int) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        tasks = await self._session.execute(select(Task).join(Category).where(Category.users.any(id=user_id)))
        return tasks.scalars().all()

    async def get_all_tasks(self) -> list[Task]:
        """Получает все задачи."""
        tasks = await self._session.execute(select(Task))
        return tasks.scalars().all()
