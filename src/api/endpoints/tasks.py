from fastapi import APIRouter, Depends

from src.api.schemas import TaskRequest, TaskResponse
from src.api.services import TaskService
from src.bot.bot import create_bot
from src.core.db.models import Task
from src.core.services.notification import TelegramNotification
from src.core.utils import display_tasks

task_router = APIRouter()


@task_router.post("/", description="Актуализирует список задач.")
async def actualize_tasks(
    tasks: list[TaskRequest],
    task_service: TaskService = Depends(),
    notifications_services: TelegramNotification = Depends(create_bot),
) -> None:
    await task_service.actualize_objects(tasks, Task)
    await notifications_services.send_notification(message=display_tasks)


@task_router.get(
    "/{user_id}",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач из категорий на которые подписан юзер.",
)
async def get_tasks_for_user(user_id: int, task_service: TaskService = Depends()) -> list[TaskResponse]:
    return await task_service.get_tasks_for_user(user_id)


@task_router.get(
    "/",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач.",
)
async def get_all_tasks(task_service: TaskService = Depends()) -> list[TaskResponse]:
    return await task_service.get_all()
