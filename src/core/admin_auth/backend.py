from fastapi import Response
from fastapi.responses import JSONResponse
from fastapi_users import models
from fastapi_users.authentication import AuthenticationBackend, BearerTransport, JWTStrategy, Strategy
from fastapi_users.authentication.transport import Transport
from fastapi_users.types import DependencyCallable

from src.api.constants import JWT_LIFETIME_SECONDS, JWT_REFRESH_LIFETIME_SECONDS
from src.api.schemas.admin import CustomBearerResponse
from src.settings import settings


class CustomBearerTransport(BearerTransport):
    async def get_login_response(self, token: str, refresh_token: str) -> Response:
        bearer_response = CustomBearerResponse(
            access_token=token,
            refresh_token=refresh_token,
        )
        return JSONResponse(bearer_response.model_dump())


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
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=JWT_LIFETIME_SECONDS)


def get_refresh_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=settings.SECRET_KEY, lifetime_seconds=JWT_REFRESH_LIFETIME_SECONDS)


auth_backend = AuthenticationBackendRefresh(
    name="admin",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
    get_refresh_strategy=get_refresh_jwt_strategy,
)
