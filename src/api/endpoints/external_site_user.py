from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import ExternalSiteFundRequest, ExternalSiteVolunteerRequest
from src.api.services import ExternalSiteUserService
from src.core.depends import Container

site_user_router = APIRouter(dependencies=[Depends(check_header_contains_token)])


@site_user_router.post("/external_user_registration", description="Актуализирует данные волонтёра с сайта ProCharity.")
@inject
async def external_user_registration(
    site_user: ExternalSiteVolunteerRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.register(site_user)


@site_user_router.post("/external_fund_registration", description="Актуализирует данные фонда с сайта ProCharity.")
@inject
async def external_fund_registration(
    site_user: ExternalSiteFundRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.register(site_user)
