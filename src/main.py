from fastapi import FastAPI
from src.bot.bot import shutdown_bot, startup_bot
from src.core.utils import set_ngrok
from src.depends import Container
from src.settings import settings


from asgi_correlation_id import CorrelationIdMiddleware
from src.core.logging.middleware import LoggingMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.api.router import api_router

from telegram import Update
from telegram.ext import Application, TypeHandler

from src.bot.handlers import categories, feedback_form, menu, registration, tasks
from src.core.logging.utils import logging_updates

from src.core.logging.setup import setup_logging


def init_app(fastpi_app: FastAPI) -> FastAPI:
    origins = ["*"]
    fastpi_app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_logging()
    fastpi_app.add_middleware(LoggingMiddleware)
    fastpi_app.add_middleware(CorrelationIdMiddleware)

    fastpi_app.include_router(api_router)
    if settings.DEBUG:
        fastpi_app.mount(
            "/static",
            StaticFiles(directory=settings.STATIC_DIR, html=True),
            name="static",
        )
    return fastpi_app


def init_bot(telegram_bot: Application) -> Application:
    registration.registration_handlers(telegram_bot)
    categories.registration_handlers(telegram_bot)
    tasks.registration_handlers(telegram_bot)
    menu.registration_handlers(telegram_bot)
    feedback_form.registration_handlers(telegram_bot)
    telegram_bot.add_handler(TypeHandler(Update, logging_updates))
    return telegram_bot


def main(run_bot: bool = True) -> FastAPI:
    container = Container()
    container.wire(packages=(__package__,))
    fastapi_app = init_app(container.fastapi_app())
    init_bot(container.telegram_bot())

    @fastapi_app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        if run_bot:
            fastapi_app.state.bot_instance = await startup_bot()
        if settings.USE_NGROK:
            set_ngrok()

    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        if run_bot:
            await shutdown_bot(fastapi_app.state.bot_instance)

    return fastapi_app
