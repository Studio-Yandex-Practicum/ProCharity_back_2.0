from src.api.schemas import DBStatus
from src.api.services.health_check import HealthCheckService
from src.core.db.repository import UserRepository


class AnalyticsService:
    """Сервис для работы с моделью Analytics."""

    def __init__(self, user_repository: UserRepository, health_check_service: HealthCheckService) -> None:
        self._user_repository: UserRepository = user_repository
        self._health_check_service: HealthCheckService = health_check_service

    async def get_user_number(self) -> None:
        return await self._user_repository.count_all()

    async def get_count_active_tasks(self) -> None:
        db_status: DBStatus = await self._health_check_service.check_db_connection()
        last_update = db_status["last_update"]
        if not (db_status["status"] or db_status["last_update"]):
            last_update = "Unable to get last_update"
        active_tasks = db_status["active_tasks"]
        return last_update, active_tasks
