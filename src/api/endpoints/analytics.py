from fastapi import APIRouter, Depends

from src.api.schemas import Statistic
from src.api.services.analitics import get_number_users_statistic

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
async def get_statistics() -> Statistic:
    statistics = Statistic
    statistics.number_users = get_number_users_statistic()
    return statistics
