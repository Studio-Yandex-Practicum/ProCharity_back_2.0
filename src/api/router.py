from typing import Iterator, Optional

from fastapi import APIRouter, Depends, status, Request
from fastapi.responses import StreamingResponse

from src.api.schemas import CategoryRequest, CategoryResponse, TaskRequest, TaskResponse, QueryParams
from src.api.services.category import CategoryService
from src.api.services.task import TaskService
from src.core.db.models import Category, Task
from src.settings import settings

api_router = APIRouter(tags=["API"])


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


@api_router.get(
    "/telegram/feedback-form",
    status_code=status.HTTP_200_OK,
    summary="Вернуть шаблон формы обратной связи в телеграм",
    response_description="Предоставить пользователю форму для заполнения",
)
async def user_register_form_webhook(
        request: Request,
        parameters: QueryParams = Depends(QueryParams),
) -> StreamingResponse:
    """
    Вернуть пользователю в телеграм форму для заполнения персональных данных.

    - **surname**: фамилия пользователя
    - **name**: имя пользователя
    - **email**: Email
    - **question**: вопрос или предложение
    """
    headers: dict[str, str] = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0",
    }
    name = request.query_params.get('name')
    surname = request.query_params.get('surname')

    def get_feedback_form() -> Iterator[bytes]:
        """
        Открывает для чтения html-шаблон формы регистрации пользователя.
        Возвращает генератор для последующего рендеринга шаблона StreamingResponse-ом.
        """
        with open(settings.feedback_form_template, 'rb') as html_form:
            yield from html_form

    return StreamingResponse(get_feedback_form(), media_type="text/html", headers=headers)
