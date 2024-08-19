from fastapi import APIRouter

from src.api.endpoints import (
    admin_auth_router,
    admin_router,
    admin_user_router,
    category_router,
    feedback_router,
    health_check_router,
    notification_router_by_token,
    site_user_router,
    task_read_router,
    task_response_router,
    task_write_router,
    tasks_router,
    telegram_webhook_router,
)
from src.settings import settings

api_router = APIRouter(prefix=settings.ROOT_PATH)

# Порядок следующих двух строк важен для правильной обработки путей!
api_router.include_router(notification_router_by_token, prefix="/send_telegram_notification", tags=["Messages"])
api_router.include_router(admin_router)
api_router.include_router(category_router, prefix="/categories", tags=["Content"])
api_router.include_router(health_check_router, prefix="/health_check", tags=["Healthcheck"])
api_router.include_router(tasks_router, prefix="/tasks", tags=["Content"])
api_router.include_router(task_read_router, prefix="/task", tags=["Content"])
api_router.include_router(task_write_router, prefix="/task", tags=["Content"])
api_router.include_router(task_response_router, prefix="/task_response", tags=["Content"])
api_router.include_router(telegram_webhook_router, prefix="/telegram", tags=["Telegram"])
api_router.include_router(admin_auth_router, prefix="/auth", tags=["AdminAuth"])
api_router.include_router(admin_user_router, prefix="/admins", tags=["Admins"])
api_router.include_router(site_user_router, prefix="/auth/external_user_registration", tags=["ExternalSiteUser"])
api_router.include_router(feedback_router, prefix="/feedback", tags=["Feedback Form"])
