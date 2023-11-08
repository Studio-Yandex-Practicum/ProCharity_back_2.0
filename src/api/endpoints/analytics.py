from datetime import date

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import Analytic
from src.api.services.analytics import AnalyticsService
from src.depends import Container

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
@inject
async def get_analytics(
        date_limit: date = '2023-11-20',
        analytic_service: AnalyticsService = Depends(Provide[Container.analytic_service]),
) -> Analytic:
    return Analytic(
        number_users=await analytic_service.get_user_number(),
        all_users_statistic=await analytic_service.get_all_users_statistic(date_limit),
    )
