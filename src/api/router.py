from fastapi import APIRouter

from src.api.endpoints import category_router, task_router

api_router = APIRouter()

api_router.include_router(category_router, prefix="/categories", tags=["Categories"])
api_router.include_router(task_router, prefix="/tasks", tags=["Tasks"])
