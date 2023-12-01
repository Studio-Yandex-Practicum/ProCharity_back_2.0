from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.core.db import get_session
from src.settings import Settings


class DataBaseConnectionContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей DataBase connection."""

    settings = providers.Dependency(instance_of=Settings)
    engine = providers.Singleton(
        create_async_engine,
        url=settings.provided.database_url,
    )
    sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        expire_on_commit=False,
    )
    session = providers.Resource(
        get_session,
        sessionmaker=sessionmaker,
    )
