from fastapi import APIRouter

from src.api.endpoints.admin_routers.invitation import invitation_router
from src.api.fastapi_admin_users import auth_backend, auth_cookie_backend, fastapi_admin_users
from src.api.schemas.admin import AdminUserCreate, AdminUserRead

admin_user_router = APIRouter()


admin_user_router.include_router(fastapi_admin_users.get_auth_router(auth_backend))
admin_user_router.include_router(fastapi_admin_users.get_register_router(AdminUserRead, AdminUserCreate))
admin_user_router.include_router(
    fastapi_admin_users.get_auth_router(auth_cookie_backend),
    prefix="/cookies",
)
admin_user_router.include_router(fastapi_admin_users.get_reset_password_router(), prefix="", tags=["Reset Password"])
admin_user_router.include_router(invitation_router, prefix="", tags=["AdminUser"])
