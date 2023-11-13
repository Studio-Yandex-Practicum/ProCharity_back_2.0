from datetime import timedelta

from src.api.constants import DAYS_NUMBER
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

    async def get_added_users_statistic(self, date_limit) -> dict[str, int]:
        date_begin = date_limit - timedelta(days=DAYS_NUMBER - 1)
        added_users = await self._user_repository.get_statistics_by_days(date_begin, date_limit, "created_at")
        return added_users

    async def get_added_external_users_statistic(self, date_limit) -> dict[str, int]:
        date_begin = date_limit - timedelta(days=DAYS_NUMBER - 1)
        added_external_users = await self._user_repository.get_statistics_by_days(
            date_begin, date_limit, "external_signup_date"
        )
        return added_external_users

    async def get_unsubscribed_users_statistic(self, date_limit) -> dict[str, int]:
        date_begin = date_limit - timedelta(days=DAYS_NUMBER - 1)
        users_unsubscribed = await self._unsubscribe_reason_repository.get_statistics_by_days(
            date_begin, date_limit, "created_at"
        )
        return users_unsubscribed
