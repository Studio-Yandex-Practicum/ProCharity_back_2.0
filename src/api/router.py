from fastapi import APIRouter, Depends

from src.api.schemas import CaregoryRequest, CategoryResponse, TaskRequest, TaskResponse
from src.api.services.category import CategoryService
from src.api.services.task import TaskService

api_router = APIRouter()
category_router = APIRouter()
task_router = APIRouter()


@category_router.get(
    "/",
    response_model=list[CategoryResponse],
    response_model_exclude_none=True,
    description="Получает список всех категорий.",
)
async def get_category(category_service: CategoryService = Depends()):
    categories = await category_service.get_all_categories()
    return categories


@category_router.post("/", description="Актуализирует список категорий.")
async def actualize_categories(categories: list[CaregoryRequest], category_service: CategoryService = Depends()):
    await category_service.actualize_categories(categories)


@task_router.post("/", description="Актуализирует список задач.")
async def actualize_tasks(tasks: list[TaskRequest], task_service: TaskService = Depends()):
    await task_service.actualize_tasks(tasks)


@task_router.get(
    "/{user_id}",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач из категорий на которые подписан юзер.",
)
async def get_tasks_for_user(user_id: int, task_service: TaskService = Depends()):
    return await task_service.get_tasks_for_user(user_id)


@task_router.get(
    "/",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач.",
)
async def get_all_tasks(task_service: TaskService = Depends()):
    tasks = await task_service.get_all_tasks()
    return tasks


api_router.include_router(category_router, prefix="/categories", tags=["Categories"])
api_router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
