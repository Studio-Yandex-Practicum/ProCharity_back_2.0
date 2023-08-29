from dependency_injector import containers, providers
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.bot.bot import create_bot
from src.core.db import get_session
from src.settings import get_settings
from src.core.db.repository.admin_repository import AdminUserRepository
from src.api.services.admin_service import AdminService


class Container(containers.DeclarativeContainer):
    """Контейнер dependency_injector."""

    # Settings
    settings = providers.Singleton(get_settings)

    # Database connection
    engine = providers.Singleton(create_async_engine, url=settings.provided.database_url)
    sessionmaker = providers.Singleton(async_sessionmaker, bind=engine, expire_on_commit=False)
    session = providers.Resource(get_session, sessionmaker=sessionmaker)
    admin_repository = providers.Factory(AdminUserRepository, session=session)
    admin_service = providers.Factory(AdminService, admin_repository=admin_repository)

    # Applications
    fastapi_app = providers.Singleton(FastAPI, debug=settings.provided.DEBUG)
    telegram_bot = providers.Singleton(create_bot, bot_token=settings.provided.BOT_TOKEN)
