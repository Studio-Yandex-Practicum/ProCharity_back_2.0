from datetime import timedelta

from dependency_injector import containers, providers
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearer


class JWTServicesContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей JWT services."""

    settings = providers.Dependency()
    access_security = providers.Factory(
        JwtAccessBearerCookie,
        secret_key=settings.provided.SECRET_KEY,
        auto_error=False,
        access_expires_delta=timedelta(hours=1),
    )
    refresh_security = providers.Factory(
        JwtRefreshBearer,
        secret_key=settings.provided.SECRET_KEY,
        auto_error=True,
    )
