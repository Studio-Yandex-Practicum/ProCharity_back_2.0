from fastapi import Depends
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import false

from src.core.db.db import get_session
from src.core.db.models import Category, Task, User
from src.core.db.repository.base import ContentRepository


class TaskRepository(ContentRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Task)

    async def get_tasks_for_user(self, user_id: int, limit: int, offset: int) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        tasks = await self._session.execute(
            select(Task).join(Category).where(Category.users.any(id=user_id)).limit(limit).offset(offset)
        )
        return tasks.scalars().all()

    async def get_all_user_tasks(self) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        return await self._session.scalars(select(Task).options(joinedload(Task.category)))

    async def get_tasks_limit_for_user(self, limit: int, offset: int, user_telegram_id: int) -> list[Task]:
        """Получить limit-выборку из списка всех задач пользователя."""
        user_id = await self._session.scalar((select(User.id).where(User.telegram_id == user_telegram_id)))
        return await self._session.scalars(
            select(Task)
            .join(Category)
            .options(joinedload(Task.category))
            .where(and_(Category.users.any(id=user_id)), Task.is_archived == false())
            .limit(limit)
            .offset(offset)
        )

    async def get_user_tasks_count(self, user_telegram_id: int) -> int:
        """Получить общее количество задач для пользователя."""
        user_id = await self._session.scalar((select(User.id).where(User.telegram_id == user_telegram_id)))
        tasks = await self._session.scalars(
            select(Task)
            .join(Category)
            .options(joinedload(Task.category))
            .where(and_(Category.users.any(id=user_id)), Task.is_archived == false())
        )
        return len(tasks.all())
