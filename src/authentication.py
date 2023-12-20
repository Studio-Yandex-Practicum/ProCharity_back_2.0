import re
from datetime import date
from typing import AsyncGenerator, Generic, Optional, Sequence, Tuple, Type, Union

import structlog
from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.param_functions import Form
from fastapi.responses import JSONResponse
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas
from fastapi_users.authentication import AuthenticationBackend, Authenticator, BearerTransport, JWTStrategy, Strategy
from fastapi_users.authentication.transport import Transport
from fastapi_users.manager import UserManagerDependency
from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorCode, ErrorModel
from fastapi_users.schemas import model_dump
from fastapi_users.types import DependencyCallable
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing_extensions import Annotated

from src.api.constants import PASSWORD_POLICY
from src.api.schemas.admin import UserCreate
from src.api.services import AdminTokenRequestService
from src.core.db.models import AdminUser, Base
from src.core.depends import Container
from src.core.exceptions.exceptions import (
    BadRequestException,
    InvalidInvitationToken,
    InvalidPassword,
    PasswordNotProvided,
    UserAlreadyExists,
)
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
    async def create(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Optional[Request] = None,
        admin_token_request_service: AdminTokenRequestService = Depends(
            Provide[Container.api_services_container.admin_token_request_service]
        ),
    ) -> models.UP:
        token = user_create.token
        registration_record = await admin_token_request_service.get_by_token(token)
        if not registration_record or registration_record.token_expiration_date < date.today():
            await log.ainfo(f'Registration: The invitation "{token}" not found or expired.')
            raise InvalidInvitationToken
        del user_create.token

        email = registration_record.email
        existing_user = await self.user_db.get_by_email(email)
        if existing_user is not None:
            await log.ainfo(f"Registration: The user with the specified mailing address {email} is already registered.")
            raise UserAlreadyExists

        password = user_create.password
        if not password:
            await log.ainfo(f"Registration: The password for registration not passed. User: {email}")
            raise PasswordNotProvided
        await self.validate_password(password, user_create, email)

        user_dict = user_create.create_update_dict() if safe else user_create.create_update_dict_superuser()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["email"] = email

        try:
            created_user = await self.user_db.create(user_dict)
            await admin_token_request_service.remove(registration_record)
        except TypeError as ex:
            await log.ainfo(f'Registration: Database commit error "{str(ex)}"')
            raise BadRequestException(f"Bad request: {str(ex)}")

        await self.on_after_register(created_user, request)
        return JSONResponse(content={"description": "Пользователь успешно зарегистрирован."})

    async def validate_password(self, password: str, user: UserCreate | AdminUser, email: str) -> None:
        if re.match(PASSWORD_POLICY, password) is None or email in password or user.last_name in password:
            await log.ainfo(
                f"Registration: The entered password does not comply with the password policy. User: {email}."
            )
            raise InvalidPassword

    async def on_after_register(self, user: AdminUser, request: Optional[Request] = None) -> None:
        await log.ainfo(f"Registration: User {user.email} is successfully registered.")

    async def on_after_login(
        self,
        user: AdminUser,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
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


def get_register_router(
    get_user_manager: UserManagerDependency[models.UP, models.ID],
    user_schema: Type[schemas.U],
    user_create_schema: Type[schemas.UC],
) -> APIRouter:
    """Generate a router with the register route."""
    router = APIRouter()

    @router.post(
        "/register",
        status_code=status.HTTP_200_OK,
        name="User Registration",
        responses={
            status.HTTP_400_BAD_REQUEST: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            UserAlreadyExists.status_code: {
                                "summary": "The user with the specified mailing address email is already registered.",
                                "value": {"detail": UserAlreadyExists.detail},
                            },
                            InvalidPassword.status_code: {
                                "summary": "The entered password does not comply with the password policy.",
                                "value": {"detail": InvalidPassword.detail},
                            },
                        }
                    }
                },
            },
            status.HTTP_401_UNAUTHORIZED: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            PasswordNotProvided.status_code: {
                                "summary": "The password for registration not passed.",
                                "value": {"detail": PasswordNotProvided.detail},
                            },
                        }
                    }
                },
            },
            status.HTTP_403_FORBIDDEN: {
                "model": ErrorModel,
                "content": {
                    "application/json": {
                        "examples": {
                            InvalidInvitationToken.status_code: {
                                "summary": "The invitation token not found or expired.",
                                "value": {"detail": InvalidInvitationToken.detail},
                            },
                        }
                    }
                },
            },
        },
    )
    async def register(
        request: Request,
        user_create: user_create_schema,
        user_manager: BaseUserManager[models.UP, models.ID] = Depends(get_user_manager),
    ):
        try:
            message = await user_manager.create(user_create, safe=True, request=request)
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=ErrorCode.REGISTER_USER_ALREADY_EXISTS,
            )
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": ErrorCode.REGISTER_INVALID_PASSWORD,
                    "reason": e.reason,
                },
            )

        return message

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
