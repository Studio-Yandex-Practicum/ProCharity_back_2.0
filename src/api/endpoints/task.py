from fastapi import APIRouter, Depends

from src.api.schemas import TaskRequest, TaskResponse
from src.api.services.task import TaskService

router = APIRouter()


@router.post("/", description="Актуализирует список задач.")
async def actualize_tasks(tasks: list[TaskRequest], task_service: TaskService = Depends()):
    await task_service.actualize_tasks(tasks)


@router.get(
    "/{user_id}",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач из категорий на которые подписан юзер.",
)
async def get_tasks_for_user(user_id: int, task_service: TaskService = Depends()):
    return await task_service.get_tasks_for_user(user_id)


@router.get(
    "/",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач.",
)
async def get_all_tasks(task_service: TaskService = Depends()):
    tasks = await task_service.get_all_tasks()
    return tasks
