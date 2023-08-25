from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.router import api_router, tags_metadata
from src.bot.bot import shutdown_bot, startup_bot
from src.core.logging.middleware import LoggingMiddleware
from src.core.logging.setup import setup_logging
from src.core.utils import set_ngrok
from src.settings import settings


def create_app(run_bot: bool = True) -> FastAPI:
    app = FastAPI(
        debug=settings.DEBUG,
        openapi_tags=tags_metadata,
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
    if settings.DEBUG:
        app.mount(
            "/static",
            StaticFiles(directory=settings.STATIC_DIR, html=True),
            name="static",
        )

    @app.on_event("startup")
    async def on_startup():
        """Действия при запуске сервера."""
        if run_bot:
            app.state.bot_instance = await startup_bot()
        if settings.USE_NGROK:
            set_ngrok()

    @app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        if run_bot:
            await shutdown_bot(app.state.bot_instance)

    return app
