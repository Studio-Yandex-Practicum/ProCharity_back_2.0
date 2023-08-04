from fastapi import APIRouter, Depends

from src.api.schemas import Analytic
from src.api.services.analitics import AnalyticsService

analytic_router = APIRouter()


@analytic_router.get("/", response_model=Analytic, description="Возращает статистику сервиса.")
async def get_statistics(analytic_service: AnalyticsService = Depends()) -> Analytic:
    users_number = await analytic_service.get_users_number()
    statistics = Analytic
    statistics.number_users = users_number
    return statistics
