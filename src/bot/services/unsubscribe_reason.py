from src.core.db.models import UnsubscribeReason
from src.core.db.repository import UnsubscribeReasonRepository, UserRepository


class UnsubscribeReasonService:
    """Сервис для работы с моделью UnsubscribeReason."""

    def __init__(
        self, user_repository: UserRepository, unsubscribe_reason_repository: UnsubscribeReasonRepository
    ) -> None:
        self._user_repository = user_repository
        self._unsubscribe_reason_repository = unsubscribe_reason_repository

    async def save_reason(self, telegram_id: int, reason: str) -> None:
        user = await self._user_repository.get_by_telegram_id(telegram_id)
        reason_obj = await self._unsubscribe_reason_repository.get_by_user(user)
        if reason_obj is not None:
            await self._unsubscribe_reason_repository.update(
                reason_obj.id, UnsubscribeReason(user_id=user.id, unsubscribe_reason=reason)
            )
        else:
            await self._unsubscribe_reason_repository.create(UnsubscribeReason(user_id=user.id, unsubscribe_reason=reason))
