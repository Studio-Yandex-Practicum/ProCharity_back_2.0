from fastapi import APIRouter, Depends

from src.api.schemas import HealthCheck
from src.api.services.health_check import HealthCheckService
from src.core.logging.utils import logger_decor

health_check_router = APIRouter()

@logger_decor
@health_check_router.get(
    "/", description="Проверяет соединение с БД, ботом и выводит информацию о последнем коммите."
)
async def get_health_check(health_check_service: HealthCheckService = Depends()) -> HealthCheck:
    return HealthCheck(
        check_db_connection=await health_check_service.check_db_connection(),
        check_bot=await health_check_service.check_bot(),
        last_commit=await health_check_service.get_last_commit(),
    )
