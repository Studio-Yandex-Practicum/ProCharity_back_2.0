import contextlib
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository


class TaskService:
    """Сервис бота для работы с моделью Task."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session):
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def get_user_tasks(self, limit: int) -> list[Task]:
        async with self._sessionmaker() as session:
            repository = TaskRepository(session)
            return await repository.get_user_tasks(limit)

    async def get_all_user_tasks(self) -> list[Task]:
        async with self._sessionmaker() as session:
            repository = TaskRepository(session)
            tasks = await repository.get_all_user_tasks()
            return tasks.all()

    async def get_user_tasks_by_page(self, tasks, context, limit: int):
        page_number = context.user_data.get("page_number", 1)
        start = (page_number - 1) * limit
        finish = page_number * limit
        tasks_to_show = tasks[start:finish]
        return tasks_to_show, page_number
