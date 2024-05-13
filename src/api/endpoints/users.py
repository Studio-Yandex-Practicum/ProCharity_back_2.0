from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.api.fastapi_admin_users import fastapi_admin_users
from src.api.pagination import UserPaginator
from src.api.schemas import UserResponse, UsersPaginatedResponse
from src.api.services import UserService
from src.core.depends import Container
from src.settings import settings

user_router = APIRouter(
    dependencies=[
        Depends(fastapi_admin_users.current_user(optional=settings.DEBUG)),
    ]
)


@user_router.get(
    "/",
    response_model=UsersPaginatedResponse,
    response_model_exclude_none=True,
    description="Получает список всех пользователей.",
)
@inject
async def get_all_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    user_service: UserService = Depends(Provide[Container.api_services_container.user_service]),
    user_paginate: UserPaginator = Depends(Provide[Container.api_paginate_container.user_paginate]),
) -> UsersPaginatedResponse:
    users = await user_service.get_users_by_page(page, limit)
    return await user_paginate.paginate(users, page, limit, settings.users_url)


@user_router.get(
    "/{telegram_id}",
    response_model=UserResponse | None,
    response_model_exclude_none=True,
    description="Получает пользователя по его telegram_id.",
)
@inject
async def get_by_telegram_id(
    telegram_id: int, user_service: UserService = Depends(Provide[Container.api_services_container.user_service])
) -> UserResponse | None:
    return await user_service.get_by_telegram_id(telegram_id)
