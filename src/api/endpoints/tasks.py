from fastapi import APIRouter, Depends

from src.api.schemas import TaskRequest, TaskResponse
from src.api.services import TaskService
from src.api.services.messages import TelegramNotificationService
from src.core.db.models import Task
from src.core.utils import display_tasks

task_router = APIRouter()


@task_router.post("/", description="Актуализирует список задач.")
async def actualize_tasks(
    tasks: list[TaskRequest],
    task_service: TaskService = Depends(),
    telegram_notification_service: TelegramNotificationService = Depends(),
) -> None:
    await task_service.actualize_objects(tasks, Task)
    for task in tasks:
        added_task = await task_service.get_task_category_by_id(task.id)
        message = display_tasks(added_task)
        await telegram_notification_service.send_messages_to_subscribed_users(message, task.category_id)


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
