from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository
from src.core.db.repository.user import UserRepository


class TaskService:
    """Сервис бота для работы с моделью Task."""

    def __init__(self, task_repository: TaskRepository, user_repository: UserRepository):
        self._task_repository = task_repository
        self._user_repository = user_repository

    async def get_or_none(self, task_id: int) -> Task | None:
        return await self._task_repository.get_or_none(task_id)

    async def get_user_tasks_by_page(self, page_number: int, limit: int, telegram_id: int) -> list[Task]:
        offset = (page_number - 1) * limit
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        return await self._task_repository.get_tasks_limit_for_user(limit, offset, user), offset, page_number

    async def get_remaining_user_tasks_count(self, limit: int, offset: int, telegram_id: int) -> int:
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        total_tasks = await self._task_repository.get_user_tasks_count(user)
        remaining_tasks = total_tasks - (offset + limit)
        return remaining_tasks

    async def get_task_by_id(self, task_id: int) -> Task | None:
        return await self._task_repository.get_task_with_category_by_task_id(task_id)
