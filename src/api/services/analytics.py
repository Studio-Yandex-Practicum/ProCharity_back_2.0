from src.api.schemas import ReasonCancelingStatistics
from src.core.db.repository import UnsubscribeReasonRepository, UserRepository


class AnalyticsService:
    """Сервис для работы с моделью Analytics."""

    def __init__(
        self,
        user_repository: UserRepository,
        unsubscribe_reason_repository: UnsubscribeReasonRepository,
    ) -> None:
        self._user_repository: UserRepository = user_repository
        self._unsubscribe_reason_repository: UnsubscribeReasonRepository = unsubscribe_reason_repository

    async def get_user_number(self) -> None:
        return await self._user_repository.count_all()

    async def get_reason_cancelling_statistics(self) -> ReasonCancelingStatistics:
        reasons_statistic_from_db = await self._unsubscribe_reason_repository.get_reason_cancelling_statistics()
        return ReasonCancelingStatistics(**dict(reasons_statistic_from_db), exclude_unset=True)
