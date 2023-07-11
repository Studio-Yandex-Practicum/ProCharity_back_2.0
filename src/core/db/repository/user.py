from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.db.models import Category, User
from src.core.db.repository.base import AbstractRepository


class UserRepository(AbstractRepository):
    """Репозиторий для работы с моделью User."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, User)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Возвращает пользователя (или None) по telegram_id."""
        user = await self._session.execute(select(User).where(User.telegram_id == telegram_id))
        return user.scalars().first()

    async def restore_existing_user(self, user: User, username: str, first_name: str, last_name: str) -> User:
        """Обновляет данные пользователя, который уже был в базе.

        Если ранее существовавший юзер делает /start в боте, то проверяются/обновляются его username, first_name,
        last_name и сбрасывается флаг "banned" - признак, что бот у него был заблокирован.
        """
        if user.username != username or user.first_name != first_name or user.last_name != last_name or user.banned:
            user.username, user.first_name, user.last_name, user.banned = username, first_name, last_name, False
            await self.update(user.id, user)
        return user

    async def set_categories_to_user(self, telegram_id: int, categories_ids: list[int]) -> None:
        """Присваивает пользователю список категорий."""
        user = await self._session.scalar(
            select(User).options(selectinload(User.categories)).where(User.telegram_id == telegram_id)
        )

        categories = (
            (await self._session.scalars(select(Category).where(Category.id.in_(categories_ids)))).all()
            if categories_ids
            else []
        )

        user.categories = categories
        if user:
            await self.update(user.id, user)

    async def get_user_categories(self, user: User) -> list[Category]:
        """Возвращает список категорий пользователя."""
        return await self._session.scalars(select(Category).join(User.categories).where(User.id == user.id))

    async def set_mailing(self, user: User, has_mailing: bool) -> None:
        """
        Присваивает пользователю статус получения
        почтовой рассылки на задания.
        """
        user.has_mailing = has_mailing
        await self.update(user.id, user)
