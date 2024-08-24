from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.api.auth import check_header_contains_token
from src.api.schemas import TaskRequest, TaskResponse, TasksRequest, UserResponseToTaskRequest
from src.api.services import ExternalSiteUserService, TaskService
from src.api.services.messages import TelegramNotificationService
from src.bot.keyboards import get_task_info_keyboard
from src.core.db.models import Task, User
from src.core.depends import Container
from src.core.messages import display_task
from src.core.services.notification import TelegramMessageTemplate

tasks_router = APIRouter(dependencies=[Depends(check_header_contains_token)])
task_read_router = APIRouter()
task_write_router = APIRouter(dependencies=[Depends(check_header_contains_token)])
task_response_router = APIRouter(dependencies=[Depends(check_header_contains_token)])


class TaskInfoMessageTemplate(TelegramMessageTemplate):
    """Шаблон телеграм-сообщения с информацией о задаче."""

    def __init__(self, task: Task, updated_task: bool = False):
        self.task = task
        self.text = display_task(task, updated_task)

    async def render(self, user: User) -> dict:
        """Возвращает словарь с атрибутами text и reply_markup телеграм-сообщения
        с информацией о задаче, предназначенного для заданного пользователя.
        """
        site_user = user.external_user
        if site_user is None:
            return {}

        return dict(
            text=self.text,
            reply_markup=await get_task_info_keyboard(self.task, site_user),
        )


@tasks_router.post("", description="Актуализирует список задач.")
@inject
async def actualize_tasks(
    tasks: TasksRequest,
    task_service: TaskService = Depends(Provide[Container.api_services_container.task_service]),
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
    trigger_mailing_fields: str = Depends(Provide[Container.settings.provided.TRIGGER_MAILING_FIELDS]),
) -> None:
    new_tasks_ids, updated_tasks_ids = await task_service.actualize_objects(tasks.root, Task, trigger_mailing_fields)
    updated_tasks_ids_set = set(updated_tasks_ids)
    mailing_category_tasks = await task_service.get_tasks_with_categories_by_tasks_ids(
        new_tasks_ids + updated_tasks_ids
    )
    for task in mailing_category_tasks:
        await telegram_notification_service.send_task_to_users_with_category(
            task.category_id, TaskInfoMessageTemplate(task, task.id in updated_tasks_ids_set)
        )


@tasks_router.get(
    "/{user_id}",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач из категорий, на которые подписан пользователь.",
)
@inject
async def get_tasks_for_user(
    user_id: int,
    task_service: TaskService = Depends(Provide[Container.api_services_container.task_service]),
) -> list[TaskResponse]:
    return await task_service.get_tasks_for_user(user_id)


@tasks_router.get(
    "",
    response_model=list[TaskResponse],
    response_model_exclude_none=True,
    description="Получает список всех задач.",
)
@inject
async def get_all_tasks(
    task_service: TaskService = Depends(Provide[Container.api_services_container.task_service]),
) -> list[TaskResponse]:
    return await task_service.get_all()


@task_read_router.get(
    "/{task_id}",
    response_model=TaskResponse,
    response_model_exclude_none=True,
    description="Получает данные по указанной задаче.",
)
@inject
async def get_task_detail(
    task_id: int,
    task_service: TaskService = Depends(Provide[Container.api_services_container.task_service]),
) -> TaskResponse:
    return await task_service.get(task_id, is_archived=None)


@task_write_router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    description="Добавление новой задачи.",
)
@inject
async def create_task(
    task: TaskRequest,
    task_service: TaskService = Depends(Provide[Container.api_services_container.task_service]),
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
):
    await task_service.create(**task.model_dump())
    task_with_category = await task_service.get_task_with_category_by_task_id(task.id)
    if task_with_category:
        await telegram_notification_service.send_task_to_users_with_category(
            task_with_category.category_id,
            TaskInfoMessageTemplate(task_with_category),
        )


@task_write_router.patch(
    "/{task_id}",
    status_code=status.HTTP_200_OK,
    description="Обновление существующей задачи.",
)
@inject
async def update_task(
    task: TaskRequest,
    task_id: int,
    task_service: TaskService = Depends(Provide[Container.api_services_container.task_service]),
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
    trigger_mailing_fields: str = Depends(Provide[Container.settings.provided.TRIGGER_MAILING_FIELDS]),
):
    task_obj = await task_service.get(task_id, is_archived=None)
    trigger_fields_changed = await task_service.update(
        task_obj, trigger_mailing_fields, **task.model_dump(), is_archived=False
    )
    if trigger_fields_changed:
        task_with_category = await task_service.get_task_with_category_by_task_id(task_id)
        if task_with_category:
            await telegram_notification_service.send_task_to_users_with_category(
                task_with_category.category_id,
                TaskInfoMessageTemplate(task_with_category, updated_task=True),
            )


@task_write_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Архивирует указанную задачу в БД бота.",
)
@inject
async def delete_task(
    task_id: int,
    task_service: TaskService = Depends(Provide[Container.api_services_container.task_service]),
) -> None:
    await task_service.archive(task_id)


@task_response_router.post("", description="Изменяет отклик пользователя на задачу.")
@inject
async def change_user_response_to_task(
    user_response_to_task: UserResponseToTaskRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.change_user_response_to_task(
        user_response_to_task.user_id, user_response_to_task.task_id, user_response_to_task.status
    )
