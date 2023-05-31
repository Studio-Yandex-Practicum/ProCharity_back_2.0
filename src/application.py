from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.bot.bot import start_bot
from src.core.logging.middleware import LoggingMiddleware
from src.core.logging.setup import setup_logging
from src.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(
        debug=settings.DEBUG,
        docs_url="/api/docs",
    )
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    setup_logging()
    app.add_middleware(LoggingMiddleware)
    app.add_middleware(CorrelationIdMiddleware)

    app.include_router(api_router)

    @app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        bot_instance = await start_bot()
        # storing bot_instance to extra state of FastAPI app instance
        # refer to https://www.starlette.io/applications/#storing-state-on-the-app-instance
        app.state.bot_instance = bot_instance

    @app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        bot_instance = app.state.bot_instance
        # manually stopping bot updater when running in polling mode
        # see https://github.com/python-telegram-bot/python-telegram-bot/blob/master/telegram/ext/_application.py#L523
        if not settings.BOT_WEBHOOK_MODE:
            await bot_instance.updater.stop()
        await bot_instance.stop()
        await bot_instance.shutdown()

    return app
