from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

from src.api.endpoints import (
    category_router,
    form_router,
    site_user_router,
    task_router,
    users_group_notification_router,
)
from src.settings import settings

api_router = APIRouter(prefix=settings.ROOT_PATH)
api_router.include_router(category_router, prefix="/categories", tags=["Categories"])
api_router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(form_router, prefix="/telegram", tags=["Forms"])
api_router.include_router(users_group_notification_router, prefix="/messages", tags=["Messages"])
api_router.include_router(site_user_router, prefix="/external_user_registration", tags=["ExternalSiteUser"])
api_router.mount("/static", StaticFiles(directory=settings.STATIC_URL), name="static")
