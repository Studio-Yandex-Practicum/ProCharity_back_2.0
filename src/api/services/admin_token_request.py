from datetime import datetime

import structlog

from src.core.db.models import AdminTokenRequest
from src.core.db.repository.admin_token_request import AdminTokenRequestRepository
from src.core.exceptions.exceptions import InvalidInvitationToken

log = structlog.get_logger()


class AdminTokenRequestService:
    """Сервис для работы с моделью AdminTokenRequest."""

    def __init__(self, admin_token_request_repository: AdminTokenRequestRepository) -> None:
        self._repository: AdminTokenRequestRepository = admin_token_request_repository

    async def get_by_token(self, token: str) -> AdminTokenRequest | None:
        registration_record = await self._repository.get_by_token(token)
        if not registration_record or registration_record.token_expiration_date < datetime.now():
            await log.ainfo(f'Registration: The invitation "{token}" not found or expired.')
            raise InvalidInvitationToken
        return registration_record

    async def remove(self, instance: AdminTokenRequest) -> None:
        await self._repository.remove(instance)
