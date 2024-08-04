from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import AdminUserRead
from src.api.services import AdminService
from src.core.db.models import AdminUser
from src.core.depends import Container

admin_user_list_router = APIRouter()


@admin_user_list_router.get("", response_model=list[AdminUserRead])
@inject
async def list_admin_users(
    admin_user_service: AdminService = Depends(Provide[Container.api_services_container.admin_service]),
) -> list[AdminUser]:
    return await admin_user_service.get_all()
