import contextlib
from typing import Generator, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository
from src.core.db.repository.user import UserRepository


class TaskService:
    """Сервис бота для работы с моделью Task."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session):
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def get_user_tasks_by_page(self, page_number: int, limit: int, telegram_id: int) -> list[Task]:
        offset = (page_number - 1) * limit
        async with self._sessionmaker() as session:
            repository = TaskRepository(session)
            user_repository = UserRepository(session)
            user = await user_repository.get_by_telegram_id(telegram_id)
            return await repository.get_tasks_limit_for_user(limit, offset, user), offset, page_number

    async def get_remaining_user_tasks_count(self, limit: int, offset: int, telegram_id: int) -> int:
        async with self._sessionmaker() as session:
            repository = TaskRepository(session)
            user_repository = UserRepository(session)
            user = await user_repository.get_by_telegram_id(telegram_id)
            total_tasks = await repository.get_user_tasks_count(user)
            remaining_tasks = total_tasks - (offset + limit)
            return remaining_tasks

    async def get_task_by_id(self, task_id: int) -> Optional[Task]:
        async with self._sessionmaker() as session:
            repository = TaskRepository(session)
            return await repository.get_user_task_id(task_id)
