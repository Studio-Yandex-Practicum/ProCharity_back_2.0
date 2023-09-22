from http import HTTPStatus

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import AdminUserRequest
from src.api.services.admin_service import AdminService
from src.depends import Container

admin_user_router = APIRouter()


@admin_user_router.post("/", description="Логин для админа")
@inject
def auth(
    admin_data: AdminUserRequest,
    admin_service: AdminService = Depends(
        Provide[Container.admin_service],
    ),
    access_security=Depends(
        Provide[Container.access_security],
    ),
    refresh_security=Depends(
        Provide[Container.refresh_security],
    ),
):
    user = admin_service.authenticate_user(admin_data.email, admin_data.password)
    if user is None:
        return HTTPStatus.BAD_REQUEST("Неверный почтовый адрес или пароль.")
    data = {"email": admin_data.email, "password": admin_data.password}
    access_token = access_security.create_access_token(subject=data)
    refresh_token = refresh_security.create_refresh_token(subject=data)
    return {"access_token": access_token, "refresh_token": refresh_token}
