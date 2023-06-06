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
