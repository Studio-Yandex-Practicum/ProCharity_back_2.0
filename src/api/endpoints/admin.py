from fastapi import APIRouter

from src.api.schemas.admin import UserCreate, UserRead
from src.authentication import auth_backend, auth_cookie_backend, fastapi_users

admin_user_router = APIRouter()


admin_user_router.include_router(fastapi_users.get_auth_router(auth_backend))
admin_user_router.include_router(fastapi_users.get_register_router(UserRead, UserCreate))
admin_user_router.include_router(
    fastapi_users.get_auth_router(auth_cookie_backend),
    prefix="/auth/cookies",
    tags=["Admin Login Logout By Cookies"],
)