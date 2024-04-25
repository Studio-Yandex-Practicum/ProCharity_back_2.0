from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.api.schemas import UserResponse
from src.api.services import UserService
from src.authentication import fastapi_users
from src.core.depends import Container
from src.settings import settings

user_router = APIRouter(
    dependencies=[
        Depends(fastapi_users.current_user(optional=settings.DEBUG)),
    ]
)


@user_router.get(
    "",
    response_model=dict,
    response_model_exclude_none=True,
    description="Получает список всех пользователей.",
)
@inject
async def get_all_users(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    user_service: UserService = Depends(Provide[Container.api_services_container.user_service]),
) -> dict:
    return await user_service.get_users_by_page(page, limit)


@user_router.get(
    "/{user_id}",
    response_model=UserResponse | None,
    response_model_exclude_none=True,
    description="Получает пользователя по его id.",
)
@inject
async def get_by_user_id(
    user_id: int,
    user_service: UserService = Depends(Provide[Container.api_services_container.user_service]),
) -> UserResponse | None:
    return await user_service.get_by_user_id(user_id)
