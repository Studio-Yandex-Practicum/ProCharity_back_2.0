from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import ContentService
from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository


class TaskService(ContentService):
    """Сервис для работы с моделью Task."""

    def __init__(self, task_repository: TaskRepository, session: AsyncSession) -> None:
        super().__init__(task_repository, session)

    async def get_tasks_for_user(self, user_id: int) -> list[Task]:
        return await self._repository.get_tasks_for_user(user_id)

    async def get_user_task_id(self, task_id: int) -> list[Task]:
        return await self._repository.get_user_task_id(task_id)

    async def get_user_tasks_ids(self, ids: list[int]) -> list[Task]:
        return await self._repository.get_user_tasks_ids(ids)

    async def get_tasks_by_filter(self, **filter_by) -> list[Task]:
        return await self._repository.get_tasks_by_filter(**filter_by)
