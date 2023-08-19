from dependency_injector import containers, providers
from src.bot.bot import create_bot

from src.settings import get_settings
from src.core.db import get_session
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings = providers.Singleton(get_settings)
    engine = providers.Singleton(create_async_engine, url=settings.provided.database_url)
    sessionmaker = providers.Singleton(async_sessionmaker)
    session = providers.Resource(get_session)
    fastapi_app = providers.Singleton(FastAPI, debug=settings.provided.DEBUG)
    telegram_bot = providers.Singleton(create_bot)
