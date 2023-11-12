from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import ActiveTasks, Analytic
from src.api.services.analytics import AnalyticsService
from src.depends import Container

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
@inject
async def get_analytics(analytic_service: AnalyticsService = Depends(Provide[Container.analytic_service])) -> Analytic:
    return Analytic(number_users=await analytic_service.get_user_number(), tasks=await get_active_tasks_analytic())


@inject
async def get_active_tasks_analytic(
    analytic_service: AnalyticsService = Depends(Provide[Container.analytic_service]),
) -> ActiveTasks:
    last_update, active_tasks = await analytic_service.get_count_active_tasks()
    return ActiveTasks(last_update=last_update, active_tasks=active_tasks)
