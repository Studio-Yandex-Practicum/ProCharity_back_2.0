from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import HealthCheck
from src.api.services.health_check import HealthCheckService
from src.core.depends.container import Container
from src.core.logging.utils import logger_decor

health_check_router = APIRouter(dependencies=[Depends(check_header_contains_token)])


@logger_decor
@health_check_router.get("/", description="Проверяет соединение с БД, ботом и выводит информацию о последнем коммите.")
@inject
async def get_health_check(
    health_check_service: HealthCheckService = Depends(Provide[Container.api_services_container.health_check_service]),
) -> HealthCheck:
    return HealthCheck(
        db=await health_check_service.check_db_connection(),
        bot=await health_check_service.check_bot(),
        git=await health_check_service.get_last_commit(),
    )
