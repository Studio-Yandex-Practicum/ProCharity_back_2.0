from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, status

from src.api.auth import check_header_contains_token
from src.api.schemas import (
    ExternalSiteFundPartialUpdate,
    ExternalSiteFundRequest,
    ExternalSiteVolunteerPartialUpdate,
    ExternalSiteVolunteerRequest,
)
from src.api.services import ExternalSiteUserService
from src.core.depends import Container

site_user_router = APIRouter(dependencies=[Depends(check_header_contains_token)])


@site_user_router.post("/volunteer", description="Актуализирует данные волонтёра с сайта ProCharity.")
@inject
async def external_user_registration(
    site_user: ExternalSiteVolunteerRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.register(site_user)


@site_user_router.post("/fund", description="Актуализирует данные фонда с сайта ProCharity.")
@inject
async def external_fund_registration(
    site_user: ExternalSiteFundRequest,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.register(site_user)


@site_user_router.patch("/volunteer/{user_id}", description="Обновляет данные волонтёра с сайта ProCharity.")
@inject
async def external_user_partial_update(
    user_id: int,
    site_user: ExternalSiteVolunteerPartialUpdate,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.partial_update(user_id, site_user)


@site_user_router.patch("/fund/{user_id}", description="Обновляет данные фонда с сайта ProCharity.")
@inject
async def external_fund_partial_update(
    user_id: int,
    site_user: ExternalSiteFundPartialUpdate,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.partial_update(user_id, site_user)


@site_user_router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    description="Архивирует данные пользователя сайта ProCharity в БД бота.",
)
@inject
async def external_user_delete(
    user_id: int,
    site_user_service: ExternalSiteUserService = Depends(Provide[Container.api_services_container.site_user_service]),
) -> None:
    await site_user_service.archive(user_id)
