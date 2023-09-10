from src.core.db.models import UnsubscribeReason
from src.core.db.repository import UnsubscribeReasonRepository, UserRepository


class UnsubscribeReasonService:
    """Сервис для работы с моделью UnsubscribeReason."""

    def __init__(self, user_repository: UserRepository, reason_repository: UnsubscribeReasonRepository) -> None:
        self._user_repository = user_repository
        self._reason_repository = reason_repository

    async def save_reason(self, telegram_id: int, reason: str) -> None:
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        is_exists = await self._reason_repository.get_by_user(user)
        if is_exists:
            await self._reason_repository.update(is_exists.id, UnsubscribeReason(user=user.id, unsubscribe_reason=reason))
        await self._reason_repository.create(UnsubscribeReason(user=user.id, unsubscribe_reason=reason))

