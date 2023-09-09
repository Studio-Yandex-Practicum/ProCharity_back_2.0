import contextlib
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db import get_session
from src.core.db.models import UnsubscribeReason
from src.core.db.repository import UnsubscribeReasonRepository, UserRepository


class UnsubscribeReasonService:
    """Сервис для работы с моделью UnsubscribeReason."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session) -> None:
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def save_reason(self, telegram_id: int, reason: str):
        async with self._sessionmaker() as session:
            user_repository = UserRepository(session)
            reason_repository = UnsubscribeReasonRepository(session)
            user = await user_repository.get_by_telegram_id(telegram_id)
            return await reason_repository.create(UnsubscribeReason(user=user.id, unsubscribe_reason=reason))
