from datetime import datetime, timedelta

from src.api.schemas import AllUsersStatistic
from src.core.db.repository import UnsubscribeReasonRepository, UserRepository

DAYS_NUMBER = 30


class AnalyticsService:
    """Сервис для работы с моделью Analytics."""

    def __init__(
            self,
            user_repository: UserRepository,
            unsubscribe_reason_repository: UnsubscribeReasonRepository,
    ) -> None:
        self._user_repository: UserRepository = user_repository
        self._unsubscribe_reason_repository: UnsubscribeReasonRepository = (
            unsubscribe_reason_repository)

    async def get_user_number(self) -> None:
        return await self._user_repository.count_all()

    async def get_all_users_statistic(self, date_limit) -> AllUsersStatistic:
        date_begin = date_limit - timedelta(days=DAYS_NUMBER - 1)
        added_users = await self._user_repository.get_statistics_by_days(
            date_begin, date_limit, 'created_at')
        added_external_users = await self._user_repository.get_statistics_by_days(
            date_begin, date_limit, 'external_signup_date')
        users_unsubscribed = await self._unsubscribe_reason_repository.get_statistics_by_days(
            date_begin, date_limit, 'created_at')
        return {'added_users': added_users,
                'added_external_users': added_external_users,
                'users_unsubscribed': users_unsubscribed}
