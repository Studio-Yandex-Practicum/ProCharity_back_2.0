from fastapi import APIRouter, Depends

from src.api.schemas import Statistic
from src.api.services.analitics import AnalyticsService

analytic_router = APIRouter()


@analytic_router.get("/", response_model=Statistic,
                     description="Возращает статистику сервиса.")
async def get_statistics(
    analytic_service: AnalyticsService = Depends()
) -> Statistic:
    users_number = await analytic_service.get_users_number()
    statistics = Statistic
    statistics.number_users = users_number
    return statistics
