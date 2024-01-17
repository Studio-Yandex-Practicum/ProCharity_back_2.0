from src.core.db.models import AdminTokenRequest
from src.core.db.repository.admin_token_request import AdminTokenRequestRepository


class AdminTokenRequestService:
    """Сервис для работы с моделью AdminTokenRequest."""

    def __init__(self, admin_token_request_repository: AdminTokenRequestRepository) -> None:
        self._repository: AdminTokenRequestRepository = admin_token_request_repository

    async def get_by_token(self, token: str) -> AdminTokenRequest | None:
        return await self._repository.get_by_token(token)

    async def remove(self, instance: AdminTokenRequest) -> None:
        await self._repository.remove(instance)
