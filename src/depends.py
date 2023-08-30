from dependency_injector import containers, providers
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.services.health_check import HealthCheckService
from src.bot.bot import create_bot
from src.core.db import get_session
from src.core.db.repository import TaskRepository
from src.settings import get_settings


class Container(containers.DeclarativeContainer):
    """Контейнер dependency_injector."""

    # Settings
    settings = providers.Singleton(get_settings)

    # Database connection
    engine = providers.Singleton(create_async_engine, url=settings.provided.database_url)
    sessionmaker = providers.Singleton(async_sessionmaker, bind=engine, expire_on_commit=False)
    session = providers.Resource(get_session, sessionmaker=sessionmaker)

    # Applications
    fastapi_app = providers.Singleton(FastAPI, debug=settings.provided.DEBUG)
    telegram_bot = providers.Singleton(create_bot, bot_token=settings.provided.BOT_TOKEN)

    # Repositories
    task_repository = providers.Factory(TaskRepository, session=session)

    # Services
    health_check_service = providers.Factory(
        HealthCheckService, task_repository=task_repository, telegram_bot=telegram_bot
    )
