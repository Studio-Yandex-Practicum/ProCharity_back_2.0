from src.api.schemas import ActiveTasks
from src.api.services.health_check import HealthCheckService
from src.core.db.repository import UserRepository


class AnalyticsService:
    """Сервис для работы с моделью Analytics."""

    def __init__(self, user_repository: UserRepository, health_check_service: HealthCheckService) -> None:
        self._user_repository: UserRepository = user_repository
        self._health_check_service: HealthCheckService = health_check_service

    async def get_user_number(self) -> None:
        return await self._user_repository.count_all()

    async def get_count_active_tasks(self) -> ActiveTasks:
        data = await self._health_check_service.check_db_connection()
        last_update = data["last_update"]
        active_tasks = data["active_tasks"]
        return ActiveTasks(last_update=last_update, active_tasks=active_tasks)
