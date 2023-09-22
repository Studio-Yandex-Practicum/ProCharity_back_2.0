from asgi_correlation_id import CorrelationIdMiddleware
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from src.api.constants import API_DESCRIPTION
from src.api.router import api_router
from src.core.logging.middleware import LoggingMiddleware
from src.core.logging.setup import setup_logging
from src.settings import settings


def init_app(fastpi_app: FastAPI) -> FastAPI:
    """Инициализация приложения FastAPI."""
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
    fastpi_app.description = API_DESCRIPTION

    fastpi_app.include_router(api_router)
    if settings.DEBUG:
        fastpi_app.mount(
            "/static",
            StaticFiles(directory=settings.STATIC_DIR, html=True),
            name="static",
        )
    return fastpi_app
