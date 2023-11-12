from dependency_injector import containers, providers
from fastapi import FastAPI

from src.api.main import init_fastapi
from src.bot import create_bot
from src.bot.main import init_bot
from src.core.depends.settings import SettingsContainer


class ApplicationsContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Applications."""

    settings = providers.Container(SettingsContainer)
    telegram_bot = providers.Singleton(
        init_bot,
        telegram_bot=providers.Singleton(
            create_bot,
            bot_token=settings.settings.provided.BOT_TOKEN,
        ),
    )
    fastapi_app = providers.Singleton(
        init_fastapi,
        fastapi_app=providers.Singleton(FastAPI, debug=settings.settings.provided.DEBUG),
        settings=settings.settings,
    )
