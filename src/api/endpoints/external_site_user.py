from fastapi import APIRouter, Depends

from src.api.schemas import ExternalSiteUserRequest
from src.api.services import ExternalSiteUserService

site_user_router = APIRouter()


@site_user_router.post("/", description="Актуализирует пользователя с сайта ProCharity.")
async def external_user_registration(
    site_user: ExternalSiteUserRequest, site_user_service: ExternalSiteUserService = Depends()
) -> None:
    await site_user_service.register(site_user)
