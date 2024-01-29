from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import ExternalSiteUserRequest
from src.api.services import ExternalSiteUserService
from src.core.depends import Container

site_user_router = APIRouter(dependencies=[Depends(check_header_contains_token)])


@site_user_router.post("/external_user_registration/", description="Актуализирует пользователя с сайта ProCharity.")
@inject
async def external_user_registration(
    site_user: ExternalSiteUserRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    if site_user.id:
        existing_user = await site_user_service.get_by_id_hash(site_user.id)
        if existing_user:
            await site_user_service.update(site_user)
        else:
            raise ValueError("ExternalSiteUser с указанным id_hash не найден.")
    else:
        await site_user_service.register(site_user)
