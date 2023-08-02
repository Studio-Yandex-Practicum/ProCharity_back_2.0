from fastapi import APIRouter, Depends

from src.api.schemas import Statistic

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает количество пользователей.")
async def get_statistics() -> Statistic:
    pass
