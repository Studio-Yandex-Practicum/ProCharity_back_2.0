from fastapi import APIRouter

from src.api.endpoints import category_router, notification_router, site_user_router, task_router, analytic_router
from src.settings import settings

api_router = APIRouter(prefix=settings.ROOT_PATH)
api_router.include_router(category_router, prefix="/categories", tags=["Categories"])
api_router.include_router(analytic_router, prefix="/analytics", tags=["Statistic"])
api_router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(notification_router, prefix="/messages", tags=["Messages"])
api_router.include_router(site_user_router, prefix="/external_user_registration", tags=["ExternalSiteUser"])
