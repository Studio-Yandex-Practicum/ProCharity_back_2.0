import uuid
from datetime import datetime, timedelta

import structlog

from src.core.db.models import AdminTokenRequest
from src.core.db.repository.admin_token_request import AdminTokenRequestRepository
from src.core.exceptions.exceptions import InvalidInvitationToken
from src.settings import settings

log = structlog.get_logger()


class AdminTokenRequestService:
    """Сервис для работы с моделью AdminTokenRequest."""

    def __init__(self, admin_token_request_repository: AdminTokenRequestRepository) -> None:
        self._repository: AdminTokenRequestRepository = admin_token_request_repository

    async def get_by_token(self, token: str) -> AdminTokenRequest | None:
        """Проверяет наличие и валидность пригласительного токена и возвращает соответствующие данные."""
        registration_record = await self._repository.get_by_token(token)
        if not registration_record or registration_record.token_expiration_date < datetime.now():
            await log.ainfo(f'Registration: The invitation "{token}" not found or expired.')
            raise InvalidInvitationToken
        return registration_record

    async def create_invitation_token(self, email: str, is_superuser: bool) -> str:
        """Генерирует токен и передает данные в репозиторий."""
        token_expiration = settings.TOKEN_EXPIRATION
        token_expiration_date = datetime.now() + timedelta(seconds=token_expiration)
        token = str(uuid.uuid4())

        await self._repository.create_invitation_token(
            email=email, is_superuser=is_superuser, token=token, token_expiration_date=token_expiration_date
        )
        await log.ainfo(f'Registration: The invitation "{token}" generated for {email}.')
        return token

    async def remove(self, instance: AdminTokenRequest) -> None:
        """Передает в репозиторий объект для удаления."""
        await self._repository.remove(instance)
