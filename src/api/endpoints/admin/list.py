from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query, Request

from src.api.pagination import AdminUserPaginator
from src.api.schemas import AdminUsersPaginatedRead
from src.api.services import AdminService
from src.core.depends import Container

admin_user_list_router = APIRouter()


@admin_user_list_router.get(
    "",
    response_model=AdminUsersPaginatedRead,
    response_model_exclude_none=True,
    description="Получает список всех администраторов.",
)
@inject
async def list_admin_users(
    request: Request,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=20, ge=1),
    admin_user_service: AdminService = Depends(Provide[Container.api_services_container.admin_service]),
    admin_user_paginator: AdminUserPaginator = Depends(Provide[Container.api_paginate_container.admin_user_paginate]),
) -> AdminUsersPaginatedRead:
    admin_users = await admin_user_service.get_admin_users_by_page(page, limit)
    return await admin_user_paginator.paginate(admin_users, page, limit, request.url.path)
