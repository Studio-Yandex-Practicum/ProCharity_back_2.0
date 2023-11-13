from datetime import date

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.api.schemas import AllUsersStatistic, Analytic
from src.api.services.analytics import AnalyticsService
from src.depends import Container

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
@inject
async def get_analytics(
    date_limit: date = Query(..., example="2023-10-11"),
    analytic_service: AnalyticsService = Depends(Provide[Container.analytic_service]),
) -> Analytic:
    return Analytic(
        number_users=await analytic_service.get_user_number(),
        all_users_statistic=AllUsersStatistic(
            added_users=await analytic_service.get_added_users_statistic(date_limit),
            added_external_users=await analytic_service.get_added_external_users_statistic(date_limit),
            users_unsubscribed=await analytic_service.get_unsubscribed_users_statistic(date_limit),
        ),
    )
