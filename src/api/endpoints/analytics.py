from fastapi import APIRouter, Depends

from src.api.schemas import Analytic
from src.api.services.analytics import AnalyticsService

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
async def get_analytics(analytic_service: AnalyticsService = Depends()) -> Analytic:
    return Analytic(number_users=await analytic_service.get_user_number())
