from fastapi import APIRouter, Depends

from src.api.endpoints.analytics import analytic_router
from src.api.endpoints.notification import messages_router_by_admin, notification_router_by_admin
from src.api.endpoints.users import user_router
from src.api.fastapi_admin_users import auth_backend, auth_cookie_backend, fastapi_admin_users
from src.api.permissions import is_active_user
from src.api.schemas.admin import AdminUserCreate, AdminUserRead, AdminUserUpdate

from .invitation import invitation_router
from .list import admin_user_list_router

admin_router = APIRouter(
    dependencies=[Depends(is_active_user)],
    responses={"401": {"description": "Missing token or inactive user"}},
)
admin_router.include_router(analytic_router, prefix="/analytics", tags=["Analytic"])
admin_router.include_router(messages_router_by_admin, tags=["Messages"])
admin_router.include_router(notification_router_by_admin, tags=["Messages"])
admin_router.include_router(user_router, prefix="/users", tags=["User"])
admin_router.include_router(admin_user_list_router, prefix="/admins", tags=["Admins"])


admin_auth_router = APIRouter()
admin_auth_router.include_router(fastapi_admin_users.get_auth_router(auth_backend))
admin_auth_router.include_router(fastapi_admin_users.get_register_router(AdminUserRead, AdminUserCreate))
admin_auth_router.include_router(fastapi_admin_users.get_auth_router(auth_cookie_backend), prefix="/cookies")
admin_auth_router.include_router(invitation_router)

admin_user_router = APIRouter()
admin_user_router.include_router(fastapi_admin_users.get_users_router(AdminUserRead, AdminUserUpdate))
