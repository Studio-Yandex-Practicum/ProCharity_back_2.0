from fastapi import APIRouter

from src.api.schemas.admin import UserCreate, UserRead
from src.authentication import auth_backend, fastapi_users

admin_user_router = APIRouter()

auth_router = fastapi_users.get_auth_router(auth_backend)
if auth_router is not None:
    admin_user_router.include_router(auth_router, prefix="/auth", tags=["AdminUser"])

register_router = fastapi_users.get_register_router(UserRead, UserCreate)
if register_router is not None:
    admin_user_router.include_router(register_router, prefix="/auth", tags=["auth"])
