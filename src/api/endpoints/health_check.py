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
    gag_response = {
        "db": {"status": True, "last_update": "ph", "active_tasks": 666, "db_connection_error": "ph"},
        "bot": {"status": True, "method": "ph", "url": "ph", "error": "ph"},
        "git": {"last_commit": "ph", "commit_date": "ph", "git_tags": [], "commit_error": ""},
    }
    # try:
    #     last_commit_data = await health_check_service.get_last_commit()
    #     # last_commit_data["git_tags"] = [str(tag) for tag in last_commit_data["git_tags"]]
    #     return HealthCheck(
    #         db=await health_check_service.check_db_connection(),
    #         bot=await health_check_service.check_bot(),
    #         git=last_commit_data,
    #     )
    report = []
    try:
        import os

        from git import Repo

        repo = Repo(os.getcwd())

        master = repo.head.reference
        report.append(f"master: {str(master)}")
        report.append(f"commit_date: {str(master.commit.committed_date)}")
        report.append(f"last_commit: {master.commit[:7]}")
    except Exception as exc:
        report.append(f"Exception: {type(exc)} {str(exc)}")
    finally:
        gag_response["git"]["commit_error"] = "\n".join(report)
        return gag_response
