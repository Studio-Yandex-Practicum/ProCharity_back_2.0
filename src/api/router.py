from fastapi import APIRouter, Depends

from src.api.schemas import CategoryRequest, CategoryResponse, TaskRequest, TaskResponse
from src.api.services.category import CategoryService
from src.api.services.task import TaskService
from src.core.db.models import Category, Task

api_router = APIRouter(prefix="/api", tags=["API"])


@api_router.get(
    "/categories",
    response_model=list[CategoryResponse],
    response_model_exclude_none=True,
    description="Получает список всех категорий.",
)
async def get_categories(category_service: CategoryService = Depends()) -> list[CategoryResponse]:
    return await category_service.get_all()


@api_router.post("/categories", description="Актуализирует список категорий.")
async def actualize_categories(
    categories: list[CategoryRequest], category_service: CategoryService = Depends()
) -> None:
    await category_service.actualize_objects(categories, Category)


@api_router.post("/tasks", description="Актуализирует список задач.")
async def actualize_tasks(tasks: list[TaskRequest], task_service: TaskService = Depends()) -> None:
    await task_service.actualize_objects(tasks, Task)


@api_router.get(
    "/tasks/{user_id}",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач из категорий на которые подписан юзер.",
)
async def get_tasks_for_user(user_id: int, task_service: TaskService = Depends()) -> list[TaskResponse]:
    return await task_service.get_tasks_for_user(user_id)


@api_router.get(
    "/tasks",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач.",
)
async def get_all_tasks(task_service: TaskService = Depends()) -> list[TaskResponse]:
    return await task_service.get_all()
