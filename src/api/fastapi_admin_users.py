import re
from datetime import date
from typing import AsyncGenerator, Type

import structlog
from dependency_injector.wiring import Provide
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from fastapi_users import BaseUserManager, FastAPIUsers, IntegerIDMixin, InvalidPasswordException, models, schemas
from fastapi_users.authentication import AuthenticationBackend
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.api.endpoints.admin.auth import get_auth_router
from src.api.endpoints.admin.register import get_register_router
from src.api.services import AdminService, AdminTokenRequestService
from src.core.admin_auth.backend import auth_backend
from src.core.admin_auth.cookie_backend import auth_cookie_backend
from src.core.db.models import AdminUser
from src.core.depends import Container
from src.core.exceptions import BadRequestException, UserAlreadyExists
from src.core.services.email import EmailProvider
from src.settings import settings

from .constants import PASSWORD_POLICY, PASSWORD_POLICY_EXPLANATION

log = structlog.get_logger()

engine = create_async_engine(settings.database_url)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_admin_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, AdminUser)


class UserManager(IntegerIDMixin, BaseUserManager[AdminUser, int]):
    reset_password_token_secret = settings.SECRET_KEY

    async def create_with_token(
        self,
        user_create: schemas.UC,
        safe: bool = False,
        request: Request | None = None,
        admin_token_request_service: AdminTokenRequestService = Depends(
            Provide[Container.api_services_container.admin_token_request_service]
        ),
    ) -> AdminUser:
        token = user_create.token
        registration_record = await admin_token_request_service.get_by_token(token)
        del user_create.token

        email = registration_record.email
        existing_user = await self.user_db.get_by_email(email)
        if existing_user is not None:
            await log.ainfo(f"Registration: The user with the specified mailing address {email} is already registered.")
            raise UserAlreadyExists

        password = user_create.password
        await self.validate_password(password, user_create)

        user_dict = user_create.create_update_dict() if safe else user_create.create_update_dict_superuser()
        password = user_dict.pop("password")
        user_dict["hashed_password"] = self.password_helper.hash(password)
        user_dict["email"] = email
        user_dict["is_superuser"] = registration_record.is_superuser

        try:
            created_user = await self.user_db.create(user_dict)
            await admin_token_request_service.remove(registration_record)
        except SQLAlchemyError as ex:
            await log.ainfo(f'Registration: Database commit error "{str(ex)}"')
            raise BadRequestException(f"Bad request: {str(ex)}")

        await self.on_after_register(created_user, request)
        return JSONResponse(
            content={"description": "Пользователь успешно зарегистрирован."}, status_code=status.HTTP_201_CREATED
        )

    async def validate_password(self, password: str, user: AdminUser) -> None:
        if re.match(PASSWORD_POLICY, password) is None:
            raise InvalidPasswordException(
                reason=f"Введенный пароль не соответствует политике паролей. {PASSWORD_POLICY_EXPLANATION}"
            )

    async def on_after_forgot_password(
        self,
        user: AdminUser,
        token: str,
        request: Request | None = None,
        email_provider: EmailProvider = Depends(Provide[Container.core_services_container.email_provider]),
    ) -> None:
        await email_provider.send_restore_password_link(user.email, token)

    async def on_after_register(self, user: AdminUser, request: Request | None = None) -> None:
        await log.ainfo(f"Registration: User {user.email} is successfully registered.")

    async def on_after_login(
        self,
        user: AdminUser,
        request: Request | None = None,
        response: Request | None = None,
    ) -> None:
        await self.user_db.update(user, {"last_login": date.today()})

        await log.ainfo(f"Login: The User '{user.email}' successfully logged in. Token has been generate")

    async def delete(
        self,
        user: AdminUser,
        request: Request | None = None,
        admin_service: AdminService = Depends(Provide[Container.api_services_container.admin_service]),
    ) -> None:
        await admin_service.soft_delete(user)


class CustomFastAPIUsers(FastAPIUsers[models.UP, models.ID]):
    def get_register_router(self, user_schema: Type[schemas.U], user_create_schema: Type[schemas.UC]) -> APIRouter:
        return get_register_router(self.get_user_manager, user_schema, user_create_schema)

    def get_auth_router(self, backend: AuthenticationBackend, requires_verification: bool = False) -> APIRouter:
        return get_auth_router(
            backend,
            self.get_user_manager,
            self.authenticator,
            requires_verification,
        )


async def get_user_manager(admin_db=Depends(get_admin_db)):
    yield UserManager(admin_db)


fastapi_admin_users = CustomFastAPIUsers[AdminUser, int](
    get_user_manager,
    [auth_backend, auth_cookie_backend],
)
