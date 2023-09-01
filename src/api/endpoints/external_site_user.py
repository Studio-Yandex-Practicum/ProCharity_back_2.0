from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import ExternalSiteUserRequest
from src.api.services import ExternalSiteUserService
from src.depends import Container

site_user_router = APIRouter()


@site_user_router.post("/", description="Актуализирует пользователя с сайта ProCharity.")
@inject
async def external_user_registration(
    site_user: ExternalSiteUserRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.site_user_service]),
) -> None:
    await site_user_service.register(site_user)
