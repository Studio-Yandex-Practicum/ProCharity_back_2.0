from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.constants import API_DESCRIPTION
from src.api.utils import create_token_for_main_admin
from src.core.logging.middleware import LoggingMiddleware
from src.core.logging.setup import setup_logging
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


def set_events(fastapi_app: FastAPI, run_bot: bool):
    @fastapi_app.on_event("startup")
    async def on_startup():
        from .events import startup

        await startup(fastapi_app, run_bot)
        await create_token_for_main_admin()

    @fastapi_app.on_event("shutdown")
    async def on_shutdown():
        """Действия после остановки сервера."""
        from .events import shutdown

        await shutdown(fastapi_app, run_bot)


def init_fastapi(
    fastapi_app: FastAPI,
    settings: Settings,
    run_bot: bool,
) -> FastAPI:
    """Инициализация приложения FastAPI."""

    add_middleware(fastapi_app)
    include_router(fastapi_app)
    set_events(fastapi_app, run_bot)

    fastapi_app.description = API_DESCRIPTION

    if settings.DEBUG:
        fastapi_app.mount(
            "/static",
            StaticFiles(directory=settings.STATIC_DIR, html=True),
            name="static",
        )
    return fastapi_app
