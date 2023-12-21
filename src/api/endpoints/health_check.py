from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import HealthCheck
from src.api.services.health_check import HealthCheckService
from src.core.depends import Container
from src.core.logging.utils import logger_decor

health_check_router = APIRouter(dependencies=[Depends(check_header_contains_token)])


@logger_decor
@health_check_router.get("/", description="Проверяет соединение с БД, ботом и выводит информацию о последнем коммите.")
@inject
async def get_health_check(
    health_check_service: HealthCheckService = Depends(Provide[Container.api_services_container.health_check_service]),
) -> HealthCheck:
    try:
        last_commit_data = await health_check_service.get_last_commit()
        # last_commit_data["git_tags"] = [str(tag) for tag in last_commit_data["git_tags"]]
        return HealthCheck(
            db=await health_check_service.check_db_connection(),
            bot=await health_check_service.check_bot(),
            git=last_commit_data,
        )
    except Exception as exc:
        return {
            "db": {
                "status": True,
                "last_update": "placeholder",
                "active_tasks": 666,
                "db_connection_error": "placeholder",
            },
            "bot": {"status": True, "method": "placeholder", "url": "placeholder", "error": "placeholder"},
            "git": {
                "last_commit": "placeholder",
                "commit_date": "placeholder",
                "git_tags": ["1, 2, 3", "abc"],
                "commit_error": str(exc),
            },
        }
