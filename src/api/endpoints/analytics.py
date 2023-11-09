from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import Analytic
from src.api.services.analytics import AnalyticsService
from src.api.services.health_check import HealthCheckService
from src.depends import Container

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
@inject
async def get_analytics(
    analytic_service: AnalyticsService = Depends(Provide[Container.analytic_service]),
    health_check_service: HealthCheckService = Depends(Provide[Container.health_check_service]),
) -> Analytic:
    return Analytic(
        number_users=await analytic_service.get_user_number(), tasks=await analytic_service.get_count_active_tasks()
    )
