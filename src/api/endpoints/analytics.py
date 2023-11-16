from datetime import date

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.api.schemas import ActiveTasks, AllUsersStatistic, Analytic, DBStatus
from src.api.services.analytics import AnalyticsService
from src.api.services.health_check import HealthCheckService
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
        tasks=await get_active_tasks_analytic()
    )


@inject
async def get_active_tasks_analytic(
    health_check_service: HealthCheckService = Depends(Provide[Container.health_check_service]),
) -> ActiveTasks:
    db_status: DBStatus = await health_check_service.check_db_connection()
    last_update = db_status["last_update"]
    if not (db_status["status"] or db_status["last_update"]):
        last_update = "Unable to get last_update"
    active_tasks = db_status["active_tasks"]
    return ActiveTasks(last_update=last_update, active_tasks=active_tasks)
