from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from telegram.ext import Application

from src.api.constants import API_DESCRIPTION
from src.bot import shutdown_bot, startup_bot
from src.core.logging.middleware import LoggingMiddleware
from src.core.logging.setup import setup_logging
from src.core.utils import set_ngrok
from src.settings import Settings


def add_middleware(fastapi_app: FastAPI):
    origins = ["*"]
    fastapi_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    setup_logging()
    fastapi_app.add_middleware(LoggingMiddleware)
    fastapi_app.add_middleware(CorrelationIdMiddleware)


def include_router(fastapi_app: FastAPI):
    from src.api.router import api_router

    fastapi_app.include_router(api_router)


def set_events(
    fastapi_app: FastAPI,
    settings: Settings,
    bot: Application,
    run_bot: bool,
):
    @fastapi_app.on_event("startup")
    async def on_startup():
        if settings.USE_NGROK is True:
            set_ngrok()
        if run_bot:
            fastapi_app.state.bot_instance = await startup_bot(
                bot=bot,
                bot_webhook_mode=settings.BOT_WEBHOOK_MODE,
                telegram_webhook_url=settings.telegram_webhook_url,
                secret_key=settings.SECRET_KEY,
            )

    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        if run_bot:
            await shutdown_bot(
                fastapi_app.state.bot_instance,
                bot_webhook_mode=settings.provided.BOT_WEBHOOK_MODE,
            )


def init_fastapi(
    fastapi_app: FastAPI,
    settings: Settings,
    bot: Application,
    run_bot: bool,
) -> FastAPI:
    """Инициализация приложения FastAPI."""

    add_middleware(fastapi_app)
    include_router(fastapi_app)
    set_events(fastapi_app, settings, bot, run_bot)

    fastapi_app.description = API_DESCRIPTION

    if settings.DEBUG:
        fastapi_app.mount(
            "/static",
            StaticFiles(directory=settings.STATIC_DIR, html=True),
            name="static",
        )
    return fastapi_app
