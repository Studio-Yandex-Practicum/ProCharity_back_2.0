import contextlib
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import FeedbackFormQueryParams
from src.core.db.db import get_session
from src.core.db.models import User
from src.core.db.repository.user import UserRepository


class UserService:
    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session) -> None:
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def register_user(
        self, telegram_id: int, username: str = "", first_name: str = "", last_name: str = ""
    ) -> User:
        """Регистрирует нового пользователя по telegram_id.

        Если пользователь найден, обновляет имя и флаг "заблокирован".
        """
        async with self._sessionmaker() as session:
            user_repository = UserRepository(session)
            user = await user_repository.get_by_telegram_id(telegram_id)
            if user is not None:
                return await user_repository.restore_existing_user(
                    user=user,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                )
            return await user_repository.create(
                User(telegram_id=telegram_id, username=username, first_name=first_name, last_name=last_name)
            )

    async def set_categories_to_user(self, telegram_id: int, categories_ids: list[int]) -> None:
        """Присваивает пользователю список категорий."""
        async with self._sessionmaker() as session:
            repository = UserRepository(session)
            await repository.set_categories_to_user(telegram_id, categories_ids)

    async def get_user_categories(self, telegram_id: int) -> dict[int, str]:
        """Возвращает словарь с id и name категорий пользователя по его telegram_id."""
        async with self._sessionmaker() as session:
            repository = UserRepository(session)
            user = await repository.get_by_telegram_id(telegram_id)
            categories = await repository.get_user_categories(user)
            return {category.id: category.name for category in categories}

    async def get_mailing(self, telegram_id: int) -> bool:
        """Возвращает статус подписки пользователя на почтовую рассылку."""
        async with self._sessionmaker() as session:
            repository = UserRepository(session)
            user = await repository.get_by_telegram_id(telegram_id)
            return user.has_mailing

    async def set_mailing(self, telegram_id: int) -> bool:
        """
        Присваивает пользователю получение почтовой рассылки на задания.
        Возвращает статус подписки пользователя на почтовую рассылку.
        """
        async with self._sessionmaker() as session:
            repository = UserRepository(session)
            user = await repository.get_by_telegram_id(telegram_id)
            await repository.set_mailing(user, not user.has_mailing)
            return user.has_mailing

    async def check_and_set_has_mailing_atribute(self, telegram_id: int) -> None:
        """
        Присваивает пользователю атрибут has_mailing, для получения почтовой
        рассылки на задания после выбора категорий. Предварительно
        осуществляется проверка, установлен ли этот атрибут у пользователя
        ранее.
        """
        async with self._sessionmaker() as session:
            repository = UserRepository(session)
            user = await repository.get_by_telegram_id(telegram_id)
            if not user.has_mailing:
                await repository.set_mailing(user, True)

    async def get_feedback_query_params(
        self,
        telegram_id: int
    ) -> FeedbackFormQueryParams:
        """Возвращает объект FeedbackFormQueryParams на основе имени пользователя.
        Используется для автоподстановки личных данных в форме обратной связи."""
        async with self._sessionmaker() as session:
            user = await UserRepository(session).get_by_telegram_id(telegram_id)
        return FeedbackFormQueryParams(name=user.first_name, surname=user.last_name)
