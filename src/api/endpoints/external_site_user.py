from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import ExternalSiteUserRequest
from src.api.services import ExternalSiteUserService
from src.core.depends import Container

site_user_router = APIRouter(dependencies=[Depends(check_header_contains_token)], redirect_slashes=False)


@site_user_router.post(path="/external_user_registration/", include_in_schema=False)
@site_user_router.post(path="/external_user_registration", description="Актуализирует пользователя с сайта ProCharity.")
@inject
async def external_user_registration(
    site_user: ExternalSiteUserRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.register(site_user)
