from fastapi import APIRouter

from src.authentication import UserCreate, UserRead, auth_backend, fastapi_users

admin_user_router = APIRouter()


admin_user_router.include_router(router=fastapi_users.get_auth_router(auth_backend), prefix="/auth", tags=["AdminUser"])

admin_user_router.include_router(
    router=fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
