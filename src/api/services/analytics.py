from src.core.db.repository import TaskRepository, UserRepository


class AnalyticsService:
    """Сервис для работы с моделью Analytics."""

    def __init__(self, user_repository: UserRepository, task_repository: TaskRepository) -> None:
        self._user_repository: UserRepository = (user_repository,)
        self._task_repostory: TaskRepository = task_repository

    async def get_user_number(self) -> None:
        return await self._user_repository.count_all()

    async def get_count_active_tasks(self) -> None:
        return await self._task_repostory.get_count_active_tasks()

    async def get_last_update(self) -> None:
        return await self._task_repostory.get_last_update()
