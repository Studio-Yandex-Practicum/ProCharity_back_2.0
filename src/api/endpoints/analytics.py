from datetime import date

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Query

from src.api.permissions import is_active_user
from src.api.schemas import ActiveTasks, AllUsersStatistic, Analytic, DBStatus, ReasonCancelingStatistics
from src.api.services import HealthCheckService
from src.api.services.analytics import AnalyticsService
from src.core.depends import Container

analytic_router = APIRouter(dependencies=[Depends(is_active_user)])


@analytic_router.get(
    "",
    description="Возращает статистику сервиса.",
    responses={"401": {"description": "Inactive user"}},
)
@inject
async def get_analytics(
    date_limit: date = Query(date.today(), example=f"{date.today()}"),
    analytic_service: AnalyticsService = Depends(Provide[Container.api_services_container.analytic_service]),
) -> Analytic:
    return Analytic(
        number_users=await analytic_service.get_user_number(),
        reasons_canceling=ReasonCancelingStatistics(**await analytic_service.get_reason_cancelling_statistics()),
        all_users_statistic=AllUsersStatistic(
            added_users=await analytic_service.get_added_users_statistic(date_limit),
            added_external_users=await analytic_service.get_added_external_users_statistic(date_limit),
            users_unsubscribed=await analytic_service.get_unsubscribed_users_statistic(date_limit),
        ),
        tasks=await get_active_tasks_analytic(),
    )


@inject
async def get_active_tasks_analytic(
    health_check_service: HealthCheckService = Depends(Provide[Container.api_services_container.health_check_service]),
) -> ActiveTasks:
    db_status: DBStatus = await health_check_service.check_db_connection()
    last_update = db_status["last_update"]
    if not (db_status["status"] or db_status["last_update"]):
        last_update = "Unable to get last_update"
    active_tasks = db_status["active_tasks"]
    return ActiveTasks(last_update=last_update, active_tasks=active_tasks)
