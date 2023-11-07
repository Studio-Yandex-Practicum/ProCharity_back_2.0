from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.expression import false

from src.core.db.models import Category, Task, User
from src.core.db.repository.base import ContentRepository


class TaskRepository(ContentRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Task)

    async def get_tasks_for_user(self, user_id: int, limit: int = 3, offset: int = 0) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        tasks = await self._session.execute(
            select(Task)
            .join(Category)
            .where(Category.users.any(id=user_id))
            .where(Task.is_archived == false())
            .limit(limit)
            .offset(offset)
        )
        return tasks.scalars().all()

    async def get_all_user_tasks(self) -> list[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        return await self._session.scalars(select(Task).options(joinedload(Task.category)))

    async def get_tasks_limit_for_user(self, limit: int, offset: int, user: User) -> list[Task]:
        """Получить limit-выборку из списка всех задач пользователя."""
        return await self._session.scalars(
            select(Task)
            .join(Category)
            .options(joinedload(Task.category))
            .where(Category.users.any(id=user.id))
            .where(Task.is_archived == false())
            .limit(limit)
            .offset(offset)
        )

    async def get_user_tasks_count(self, user: User) -> int:
        """Получить общее количество задач для пользователя."""
        return await self._session.scalar(
            select(func.count(Task.id))
            .join(Category)
            .where(Category.users.any(id=user.id))
            .where(Task.is_archived == false())
        )

    async def get_user_task_id(self, task_id) -> list[Task]:
        """Получить задачу по id из категорий на которые подписан пользователь."""
        task = await self._session.scalars(select(Task).options(joinedload(Task.category)).where(Task.id == task_id))
        return task.first()

    async def get_user_tasks_ids(self, ids: list[int]) -> list[Task]:
        """Получить список задач по ids из категорий на которые подписан пользователь."""
        tasks = await self._session.execute(select(Task).options(joinedload(Task.category)).where(Task.id.in_(ids)))
        return tasks.scalars().all()
