import contextlib
from typing import Generator, List

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.core.db.db import get_session
from src.core.db.models import Task


class TaskService:
    """Сервис бота для работы с моделью Task."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session):
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def get_user_tasks(self) -> List[Task]:
        async with self._sessionmaker() as session:
            tasks = await session.execute(select(Task).options(joinedload(Task.category)).limit(3))
            tasks_list = [task for task in tasks.scalars().all()]
            return tasks_list
