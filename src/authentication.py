import structlog
from typing import AsyncGenerator, Optional

from fastapi import Depends, Request, Response
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, schemas
from fastapi_users.authentication import (
    AuthenticationBackend, BearerTransport, JWTStrategy
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from src.core.db.models import AdminUser, Base
from src.settings import settings

log = structlog.get_logger()

engine = create_async_engine(settings.database_url)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_admin_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, AdminUser)


class UserRead(schemas.BaseUser[int]):
    pass


class UserCreate(schemas.BaseUserCreate):
    pass


bearer_transport = BearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name="admin",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[AdminUser, int]):
    async def on_after_login(
        self,
        user: AdminUser,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        await log.ainfo(f"Login: The User '{user.email}' successfully logged in. Token has been generate")


async def get_user_manager(admin_db=Depends(get_admin_db)):
    yield UserManager(admin_db)


fastapi_users = FastAPIUsers[AdminUser, int](
    get_user_manager,
    [auth_backend],
)
