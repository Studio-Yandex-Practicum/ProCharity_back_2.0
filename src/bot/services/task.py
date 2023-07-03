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

    async def get_user_tasks_by_page(self, page_number, limit: int) -> list[Task]:
        offset = (page_number - 1) * limit
        async with self._sessionmaker() as session:
            repository = TaskRepository(session)
            return await repository.get_tasks_limit_for_user(limit, offset), offset, page_number

    async def get_remaining_user_tasks_count(self, limit: int, offset: int) -> int:
        async with self._sessionmaker() as session:
            repository = TaskRepository(session)
            total_tasks = await repository.get_user_tasks_count()
            remaining_tasks = total_tasks - (offset + limit)
            return remaining_tasks
