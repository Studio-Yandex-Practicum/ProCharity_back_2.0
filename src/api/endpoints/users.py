from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request

from src.api.pagination import UserPaginator
from src.api.schemas import UserResponse, UsersPaginatedResponse
from src.api.schemas.users import UserFilter
from src.api.services import UserService
from src.core.depends import Container
from src.core.exceptions import NotFoundException

user_router = APIRouter()


@user_router.get(
    "/",
    response_model=UsersPaginatedResponse,
    response_model_exclude_none=True,
    description="Получает список всех пользователей.",
)
@inject
async def get_all_users(
    request: Request,
    filter: UserFilter = Depends(UserFilter),
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    user_service: UserService = Depends(Provide[Container.api_services_container.user_service]),
    user_paginate: UserPaginator = Depends(Provide[Container.api_paginate_container.user_paginate]),
) -> UsersPaginatedResponse:
    filter_by = filter.model_dump()
    users = await user_service.get_filtered_users_by_page(filter_by, page, limit)
    return await user_paginate.paginate(users, page, limit, request.url.path, filter_by)


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
    if user := await user_service.get_by_telegram_id(telegram_id):
        return user
    raise NotFoundException(object_name="User", object_id=telegram_id)
