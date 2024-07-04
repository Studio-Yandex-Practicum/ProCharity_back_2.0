from fastapi import APIRouter

from src.api.endpoints import (
    admin_user_router,
    analytic_router,
    category_router,
    feedback_router,
    health_check_router,
    notification_router,
    site_user_router,
    task_read_router,
    task_write_router,
    tasks_router,
    telegram_webhook_router,
    user_router,
)
from src.settings import settings

api_router = APIRouter(prefix=settings.ROOT_PATH)

api_router.include_router(analytic_router, prefix="/analytics", tags=["Analytic"])
api_router.include_router(category_router, prefix="/categories", tags=["Content"])
api_router.include_router(health_check_router, prefix="/health_check", tags=["Healthcheck"])
api_router.include_router(notification_router, prefix="/messages", tags=["Messages"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["Content"])
api_router.include_router(task_read_router, prefix="/task", tags=["Content"])
api_router.include_router(task_write_router, prefix="/task", tags=["Content"])
api_router.include_router(telegram_webhook_router, prefix="/telegram", tags=["Telegram"])
api_router.include_router(admin_user_router, prefix="/auth", tags=["AdminUser"])
api_router.include_router(site_user_router, prefix="/auth", tags=["ExternalSiteUser"])
api_router.include_router(user_router, prefix="/users", tags=["User"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["Feedback Form"])
