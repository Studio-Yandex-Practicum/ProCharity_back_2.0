from fastapi import Depends

from src.api.services.base import ContentService
from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository


class TaskService(ContentService):
    """Сервис для работы с моделью Task."""

    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        super().__init__(task_repository)

    async def get_tasks_for_user(self, user_id: int) -> list[Task]:
        return await self._repository.get_tasks_in_categories_which_user_subscribe(user_id)
