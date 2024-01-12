from typing import AsyncGenerator, Generic, Optional, Sequence, Tuple, Type, Union

import structlog
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.param_functions import Form
from fastapi.responses import JSONResponse
from fastapi_users import BaseUserManager, IntegerIDMixin, models, schemas
from fastapi_users.authentication import AuthenticationBackend, Authenticator, BearerTransport, JWTStrategy, Strategy
from fastapi_users.authentication.transport import Transport
from fastapi_users.manager import UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router import get_register_router
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.schemas import model_dump
from fastapi_users.types import DependencyCallable
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing_extensions import Annotated

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
        self.user_db.last_login_update()
        await log.ainfo(f"Login: The User '{user.email}' successfully logged in. Token has been generate")


async def get_user_manager(admin_db=Depends(get_admin_db)):
    yield UserManager(admin_db)


class OAuth2PasswordRequestForm:
    def __init__(
        self,
        *,
        grant_type: Annotated[
            Union[str, None],
            Form(pattern="password"),
        ] = None,
        email: Annotated[
            str,
            Form(),
        ],
        password: Annotated[
            str,
            Form(),
        ],
        scope: Annotated[
            str,
            Form(),
        ] = "",
        client_id: Annotated[
            Union[str, None],
            Form(),
        ] = None,
        client_secret: Annotated[
            Union[str, None],
            Form(),
        ] = None,
    ):
        self.grant_type = grant_type
        self.username = email
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


def get_auth_router(
    backend: AuthenticationBackend,
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    authenticator: Authenticator,
    requires_verification: bool = False,
) -> APIRouter:
    router = APIRouter()
    get_current_user_token = authenticator.current_user_token(active=True, verified=requires_verification)

    login_responses: OpenAPIResponseType = {
        status.HTTP_400_BAD_REQUEST: {
            "model": ErrorModel,
            "content": {
                "application/json": {
                    "examples": {
                        ErrorCode.LOGIN_BAD_CREDENTIALS: {
                            "summary": "Bad credentials or the user is inactive.",
                            "value": {"detail": ErrorCode.LOGIN_BAD_CREDENTIALS},
                        },
                        ErrorCode.LOGIN_USER_NOT_VERIFIED: {
                            "summary": "The user is not verified.",
                            "value": {"detail": ErrorCode.LOGIN_USER_NOT_VERIFIED},
                        },
                    }
                }
            },
        },
        **backend.transport.get_openapi_login_responses_success(),
    }

    @router.post(
        "/login",
        name=f"auth:{backend.name}.login",
        responses=login_responses,
    )
    async def login(
        request: Request,
        credentials: OAuth2PasswordRequestForm = Depends(),
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user = await user_manager.authenticate(credentials)

        if user is None or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_BAD_CREDENTIALS,
            )
        if requires_verification and not user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.LOGIN_USER_NOT_VERIFIED,
            )
        response = await backend.login(strategy, user)
        await user_manager.on_after_login(user, request, response)
        return response

    logout_responses: OpenAPIResponseType = {
        **{status.HTTP_401_UNAUTHORIZED: {"description": "Missing token or inactive user."}},
        **backend.transport.get_openapi_logout_responses_success(),
    }

    @router.post("/logout", name=f"auth:{backend.name}.logout", responses=logout_responses)
    async def logout(
        user_token: Tuple[models.UP, str] = Depends(get_current_user_token),
        strategy: Strategy[models.UP, models.ID] = Depends(backend.get_strategy),
    ):
        user, token = user_token
        return await backend.logout(strategy, user, token)

    return router


class CustomFastAPIUsers(Generic[models.UP, models.ID]):
    authenticator: Authenticator

    def __init__(
        self,
        get_user_manager: UserManagerDependency[models.UP, models.ID],
        auth_backends: Sequence[AuthenticationBackend],
    ):
        self.authenticator = Authenticator(auth_backends, get_user_manager)
        self.get_user_manager = get_user_manager
        self.current_user = self.authenticator.current_user

    def get_register_router(self, user_schema: Type[schemas.U], user_create_schema: Type[schemas.UC]) -> APIRouter:
        return get_register_router(self.get_user_manager, user_schema, user_create_schema)

    def get_auth_router(self, backend: AuthenticationBackend, requires_verification: bool = False) -> APIRouter:
        return get_auth_router(
            backend,
            self.get_user_manager,
            self.authenticator,
            requires_verification,
        )


fastapi_users = CustomFastAPIUsers[AdminUser, int](
    get_user_manager,
    [auth_backend],
)
