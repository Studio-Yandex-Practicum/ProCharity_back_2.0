from datetime import timedelta
from http import HTTPStatus
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi_jwt import (
    JwtAccessBearerCookie,
    JwtRefreshBearer,
)
from pydantic import ValidationError

from src.api.schemas import AdminUserRequest
from src.api.services import CategoryService
from src.api.services.admin_service import AdminService
from src.core.db.models import Category
from src.depends import Container

admin_user_router = APIRouter()


access_security = JwtAccessBearerCookie(
    secret_key="secret_key",
    auto_error=False,
    access_expires_delta=timedelta(hours=1)
)

refresh_security = JwtRefreshBearer(
    secret_key="secret_key", 
    auto_error=True
)

@admin_user_router.post("/auth", description="Логин для админа")
@inject
def auth(
    admin_data: AdminUserRequest,
    admin_service: AdminService = Depends(Provide[Container.admin_service],),
):
    user = admin_service.authenticate_user(admin_data.email, admin_data.password)
    if user is not None:
        data = {'email': admin_data.email, 'password': admin_data.password}
        access_token = access_security.create_access_token(subject=data)
        refresh_token = refresh_security.create_refresh_token(subject=data)
        return {"access_token": access_token, "refresh_token": refresh_token}
    else:
        return HTTPStatus.BAD_REQUEST('Неверный почтовый адрес или пароль.')