from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request, status

from src.api.pagination import TechMessagePaginator
from src.api.permissions import is_active_superuser, is_active_user
from src.api.schemas import TechMessagePaginateResponse, TechMessageRequest, TechMessageResponce
from src.core.depends import Container
from src.core.services import TechMessageService

tech_message_router = APIRouter(dependencies=[Depends(is_active_user)])


@tech_message_router.get(
    "",
    response_model=TechMessagePaginateResponse,
    response_model_exclude_none=True,
    description="Получает список технических сообщений.",
)
@inject
async def get_all_tech_messages(
    request: Request,
    was_read: bool | None = None,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    tech_message_service: TechMessageService = Depends(Provide[Container.core_services_container.tech_message]),
    tech_message_paginate: TechMessagePaginator = Depends(
        Provide[Container.api_paginate_container.tech_message_paginate]
    ),
) -> TechMessagePaginateResponse:
    filter_by = {"was_read": was_read}
    tech_messages = await tech_message_service.get_filtered_tech_messages_by_page(filter_by, page, limit)
    return await tech_message_paginate.paginate(tech_messages, page, limit, request.url.path, filter_by)


@tech_message_router.get(
    "/{message_id}",
    response_model=TechMessageResponce,
    response_model_exclude_none=True,
    description="Получает техническое сообщение.",
)
@inject
async def get_tech_message(
    message_id: int,
    tech_message_service: TechMessageService = Depends(Provide[Container.core_services_container.tech_message]),
) -> TechMessageResponce:
    return await tech_message_service.get(message_id)


@tech_message_router.patch(
    "/{message_id}",
    response_model=TechMessageResponce,
    response_model_exclude_none=True,
    description="Обновляет данные технического сообщения.",
)
@inject
async def patch_tech_message(
    message_id: int,
    tech_message_request: TechMessageRequest,
    tech_message_service: TechMessageService = Depends(Provide[Container.core_services_container.tech_message]),
) -> TechMessageResponce:
    return await tech_message_service.partial_update(message_id, tech_message_request.model_dump())


@tech_message_router.delete(
    "/{message_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Архивирует техническое сообщение.",
    dependencies=[Depends(is_active_superuser)],
)
@inject
async def delete_tech_message(
    message_id: int,
    tech_message_service: TechMessageService = Depends(Provide[Container.core_services_container.tech_message]),
) -> None:
    return await tech_message_service.archive(message_id)
