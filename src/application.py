from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api import router
from src.settings import settings


def create_app() -> FastAPI:
    app = FastAPI(debug=settings.DEBUG, root_path=settings.ROOT_PATH)
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(router=router.router, prefix='/api')

    return app
