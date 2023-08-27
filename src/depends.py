from dependency_injector import containers, providers
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.services import ExternalSiteUserService
from src.bot.bot import create_bot
from src.core.db import get_session
from src.core.db.repository.external_site_user import ExternalSiteUserRepository
from src.settings import get_settings


class Container(containers.DeclarativeContainer):
    """Контейнер dependency_injector."""

    # Settings
    settings = providers.Singleton(get_settings)

    # Database connection
    engine = providers.Singleton(create_async_engine, url=settings.provided.database_url)
    sessionmaker = providers.Singleton(async_sessionmaker, engine=engine, expire_on_commit=False)
    session = providers.Resource(get_session, sessionmaker=sessionmaker)

    # Applications
    fastapi_app = providers.Singleton(FastAPI, debug=settings.provided.DEBUG)
    telegram_bot = providers.Singleton(create_bot, bot_token=settings.provided.BOT_TOKEN)

    site_user_repository = providers.Factory(ExternalSiteUserRepository, session=session)
    site_user_service = providers.Factory(ExternalSiteUserService, site_user_repository=site_user_repository)
