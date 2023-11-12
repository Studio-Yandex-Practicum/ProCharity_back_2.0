from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import Analytic
from src.api.services.analytics import AnalyticsService
from src.core.depends.container import Container

analytic_router = APIRouter()


@analytic_router.get("/", description="Возращает статистику сервиса.")
@inject
async def get_analytics(
    analytic_service: AnalyticsService = Depends(Provide[Container.api_services_container.analytic_service]),
) -> Analytic:
    return Analytic(number_users=await analytic_service.get_user_number())
