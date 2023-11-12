import structlog
import uuid
from typing import Optional

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from src.settings import settings
from src.core.db import get_session
from src.core.db.models import AdminUser

log = structlog.get_logger()


async def get_user_db(session: AsyncSession = Depends(get_session)):
    yield SQLAlchemyUserDatabase(session, AdminUser)


bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="admin",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(UUIDIDMixin, BaseUserManager[AdminUser, uuid.UUID]):
    async def on_after_login(
        self,
        user: AdminUser,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        await log.ainfo(f"Login: The User '{user.email}' successfully logged in. Token has been generate")


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[AdminUser, uuid.UUID](
    get_user_manager,
    [auth_backend],
)