import contextlib
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import ExternalSiteUser
from src.core.db.repository.external_site_user import ExternalSiteUserRepository


class ExternalSiteUserService:
    """Сервис бота для работы с моделью ExternalSiteUser."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session):
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def get_ext_user_by_args(self, args) -> ExternalSiteUser | None:
        """Возвращает пользователя (или None) по арументам."""
        if args:
            id_hash = args[0]
            async with self._sessionmaker() as session:
                repository = ExternalSiteUserRepository(session)
                user = await repository.get_by_id_hash(id_hash)
                return user
        return None
