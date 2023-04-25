from fastapi import Depends

from src.api.schemas import TaskRequest
from src.core.db.models import Task
from src.core.db.repository.task import TaskRepository


class TaskService:
    """Сервис для работы с моделью Task."""

    def __init__(self, task_repository: TaskRepository = Depends()) -> None:
        self.__task_repository = task_repository

    async def actualize_tasks(self, tasks: list[TaskRequest]) -> None:
        to_create, to_update = [], []
        await self.__task_repository.archive_all()
        already_have = await self.__task_repository.get_all_ids()
        for task in tasks:
            if task.id not in already_have:
                to_create.append(Task(**task.dict(), archive=False))
            else:
                to_update.append({**task.dict(), "archive": False})
        if to_create:
            await self.__task_repository.create_all(to_create)
        if to_update:
            await self.__task_repository.update_all(to_update)

    async def get_all_tasks(self) -> list[Task]:
        return await self.__task_repository.get_all()

    async def get_tasks_for_user(self, user_id: int) -> list[Task]:
        return await self.__task_repository.get_tasks_in_categories_which_user_subscribe(user_id)
