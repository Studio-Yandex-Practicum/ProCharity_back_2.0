from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import ContentService
from src.core.db import get_session
from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository


class TaskService(ContentService):
    """Сервис для работы с моделью Task."""

    def __init__(
        self, task_repository: TaskRepository = Depends(), session: AsyncSession = Depends(get_session)
    ) -> None:
        super().__init__(task_repository, session)

    async def get_tasks_for_user(self, user_id: int) -> list[Task]:
        return await self._repository.get_tasks_for_user(user_id)

    async def get_user_task_id(self, task_id: int) -> list[Task]:
        return await self._repository.get_user_task_id(task_id)
