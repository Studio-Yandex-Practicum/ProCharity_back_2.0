from fastapi import APIRouter, Depends

from src.api.schemas import Analytic
from src.api.services.analitics import AnalyticsService

analytic_router = APIRouter()


@analytic_router.get("/", response_model=Analytic, description="Возращает статистику сервиса.")
async def get_statistics(analytic_service: AnalyticsService = Depends()) -> Analytic:
    return await analytic_service.get_analytic()
