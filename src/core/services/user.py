import contextlib
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import User
from src.core.db.repository.user import UserRepository


class UserService:
    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session) -> None:
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def register_user(self, telegram_id: int, username: str = "") -> User:
        """Регистрирует нового пользователя по telegram_id.

        Если пользователь найден, обновляет имя и флаг "заблокирован".
        """
        async with self._sessionmaker() as session:
            user_repository = UserRepository(session)
            user = await user_repository.get_by_telegram_id(telegram_id)
            if user is not None:
                return await user_repository.restore_existing_user(user=user, username=username)
            user = User()
            user.telegram_id = telegram_id
            user.username = username
            return await user_repository.create(user)
