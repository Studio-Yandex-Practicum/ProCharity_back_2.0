from datetime import datetime

from src.core.db.models import Task, User
from src.core.db.repository.task import TaskRepository
from src.core.db.repository.user import UserRepository


class TaskService:
    """Сервис бота для работы с моделью Task."""

    def __init__(self, task_repository: TaskRepository, user_repository: UserRepository):
        self._task_repository = task_repository
        self._user_repository = user_repository

    async def get_or_none(self, task_id: int, is_archived: bool | None = False) -> Task | None:
        return await self._task_repository.get_or_none(task_id, is_archived=is_archived)

    async def get_user_tasks_by_page(self, page_number: int, limit: int, telegram_id: int) -> list[Task]:
        offset = (page_number - 1) * limit
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        return await self._task_repository.get_tasks_limit_for_user(limit, offset, user), offset, page_number

    async def get_user_tasks_actualized_after(
        self, user: User, after_datetime: datetime, after_id: int, limit: int
    ) -> list[tuple[Task, datetime]]:
        """Возвращает первые limit заданий, доступных пользователю user и актуализированных
        после заданного момента времени after_datetime.
        За время актуализации задачи принимается наибольшее из времён: изменения задачи и назначения
        заданному пользователю категории, к которой относится задача.
        Задачи, время актуализации которых совпадает с заданным, но их id > after_id, также
        принимаются в расчёт.
        Возвращаемое значение - список пар (задача, время её актуализации).
        """
        return await self._task_repository.get_user_tasks_actualized_after(user, after_datetime, after_id, limit)

    async def count_user_tasks_actualized_after(self, user: User, after_datetime: datetime, after_id: int) -> int:
        """Возвращает количество заданий, доступных пользователю user и актуализированных
        после заданного момента времени after_datetime.
        За время актуализации задачи принимается наибольшее из времён: изменения задачи и назначения
        заданному пользователю категории, к которой относится задача.
        Задачи, время актуализации которых совпадает с заданным, но их id > after_id, также
        принимаются в расчёт.
        """
        return await self._task_repository.count_user_tasks_actualized_after(user, after_datetime, after_id)

    async def get_remaining_user_tasks_count(self, limit: int, offset: int, telegram_id: int) -> int:
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        total_tasks = await self._task_repository.get_user_tasks_count(user)
        remaining_tasks = total_tasks - (offset + limit)
        return remaining_tasks

    async def get_task_by_id(self, task_id: int) -> Task | None:
        return await self._task_repository.get_task_with_category_by_task_id(task_id)
