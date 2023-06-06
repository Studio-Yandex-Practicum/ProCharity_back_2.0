from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository


class TaskService:
    """Сервис бота для работы с моделью Task."""

    def __init__(self, task_repository: TaskRepository):
        self.task_repository = task_repository

    async def get_user_tasks(self, limit: int = 3) -> list[Task]:
        return await self.task_repository.get_user_tasks(limit)
