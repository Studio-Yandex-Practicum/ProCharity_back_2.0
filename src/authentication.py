from typing import AsyncGenerator, Optional

import structlog
from fastapi import Depends, Request, Response
from fastapi.responses import JSONResponse
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, models, schemas
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy
from fastapi_users.authentication.strategy import Strategy
from fastapi_users.authentication.transport import Transport
from fastapi_users.schemas import model_dump
from fastapi_users.types import DependencyCallable
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
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


class CustomBearerResponse(BaseModel):
    access_token: str
    refresh_token: str


class CustomBearerTransport(BearerTransport):
    async def get_login_response(self, token: str, refresh_token: str) -> Response:
        bearer_response = CustomBearerResponse(
            access_token=token,
            refresh_token=refresh_token,
        )
        return JSONResponse(model_dump(bearer_response))


class AuthenticationBackendRefresh(AuthenticationBackend):
    def __init__(
        self,
        name: str,
        transport: Transport,
        get_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
        get_refresh_strategy: DependencyCallable[Strategy[models.UP, models.ID]],
    ):
        self.name = name
        self.transport = transport
        self.get_strategy = get_strategy
        self.get_refresh_strategy = get_refresh_strategy

    async def login(
        self,
        strategy: Strategy[models.UP, models.ID],
        user: models.UP,
    ) -> Response:
        token = await strategy.write_token(user)
        refresh_strategy = self.get_refresh_strategy()
        refresh_token = await refresh_strategy.write_token(user)
        return await self.transport.get_login_response(token=token, refresh_token=refresh_token)


bearer_transport = CustomBearerTransport(tokenUrl="auth/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=3600)


def get_refresh_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=7200)


auth_backend = AuthenticationBackendRefresh(
    name="admin",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
    get_refresh_strategy=get_refresh_jwt_strategy,
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
