from fastapi import APIRouter, Depends

from src.api.schemas import Analytic, HealthCheck
from src.api.services.analytics import AnalyticsService
from src.api.services.health_check import HealthCheckService

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
async def get_analytics(analytic_service: AnalyticsService = Depends()) -> Analytic:
    return Analytic(number_users=await analytic_service.get_user_number())


@analytic_router.get(
    "/health_check", description="Проверяет соединение с БД, ботом и выводит информацию о последнем коммите."
)
async def get_health_check(health_check_service: HealthCheckService = Depends()) -> HealthCheck:
    return HealthCheck(
        check_bot=await health_check_service.check_bot(),
        last_commit=await health_check_service.get_last_commit(),
    )
