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
        # Trying to find broken link 03fa887bd0aeff54956d5130efc2d030e5b994f6

        import os

        gitlinks_folder = os.path.join(os.getcwd(), ".git", "refs")
        refs = []
        for root, folders, files in os.walk(gitlinks_folder):
            for file in files:
                path = os.path.join(root, file)
                text = None
                with open(path, "r") as current_file:
                    text = current_file.read()[:-1]
                refs.append(" ".join((path, text)))
        packed_refs_file = os.path.join(os.getcwd(), ".git", "packed-refs")
        packed_refs = []
        with open(packed_refs_file, "r") as file:
            packed_refs = file.read().splitlines()
        response_text = "666".join((f"Exception: {str(exc)}", "\nActive refs:", *refs, "\nPacked refs:" * packed_refs))

        return {
            "db": {
                "status": True,
                "last_update": "ph",
                "active_tasks": 666,
                "db_connection_error": "ph",
            },
            "bot": {"status": True, "method": "ph", "url": "ph", "error": "ph"},
            "git": {
                "last_commit": "ph",
                "commit_date": "ph",
                "git_tags": [],
                "commit_error": response_text,
            },
        }
