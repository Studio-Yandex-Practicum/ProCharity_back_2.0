from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.router import api_router
from src.core.logging.middleware import LoggingMiddleware
from src.core.logging.setup import setup_logging
from src.settings import settings
from src.run_bot import startup_bot, shutdown_bot


def create_app(run_bot: bool) -> FastAPI:
    app = FastAPI(
        debug=settings.DEBUG,
        root_path="/api")
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
        if run_bot:
            app.state.bot_instance = await startup_bot()

    @app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        if run_bot:
            await shutdown_bot(app.state.bot_instance)

    return app
