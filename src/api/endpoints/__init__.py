from .admin import admin_user_router
from .analytics import analytic_router
from .categories import category_router
from .external_site_user import site_user_router
from .feedback import feedback_router
from .health_check import health_check_router
from .notification import notification_router
from .tasks import task_detail_router, task_router
from .telegram_webhook import telegram_webhook_router
from .users import user_router

__all__ = (
    "analytic_router",
    "category_router",
    "health_check_router",
    "task_router",
    "task_detail_router",
    "telegram_webhook_router",
    "form_router",
    "notification_router",
    "site_user_router",
    "admin_user_router",
    "feedback_router",
    "user_router",
)
