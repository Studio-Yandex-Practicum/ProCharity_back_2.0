from fastapi import APIRouter

from src.settings import settings
from src.api.endpoints import category_router, form_router, task_router

api_router = APIRouter(prefix=settings.ROOT_PATH)
api_router.include_router(category_router, prefix="/categories", tags=["Categories"])
api_router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(form_router, prefix="/telegram", tags=["Forms"])
