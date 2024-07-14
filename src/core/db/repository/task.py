from collections.abc import Sequence
from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload
from sqlalchemy.sql.expression import and_, false, or_

from src.core.db.models import Category, Task, User, UsersCategories
from src.core.db.repository.base import ContentRepository


class TaskRepository(ContentRepository):
    """Репозиторий для работы с моделью Task."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Task)

    async def get_tasks_for_user(self, user_id: int, limit: int = 3, offset: int = 0) -> Sequence[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        tasks = await self._session.scalars(
            select(Task)
            .join(Category)
            .where(Category.users.any(id=user_id))
            .where(Task.is_archived == false())
            .limit(limit)
            .offset(offset)
        )
        return tasks.all()

    async def get_user_tasks_actualized_after(
        self, user: User, after_datetime: datetime, after_id: int, limit: int
    ) -> list[tuple[Task, datetime]]:
        """Возвращает первые limit заданий, доступных пользователю user и актуализированных
        после заданного момента времени after_datetime.
        За время актуализации задачи принимается наибольшее из времён: изменения задачи и назначения
        заданному пользователю категории, к которой относится задача.
        Задачи, время актуализации которых совпадает с заданным, но их id > after_id, также
        принимаются в расчёт.
        Возвращаемое значение - список пар (задача, время её актуализации).
        """
        select_statement = (
            select(Task, func.greatest(UsersCategories.updated_at, Task.updated_at))
            .select_from(Task)
            .join(Category)
            .join(UsersCategories)
            .options(contains_eager(Task.category))
            .where(UsersCategories.user_id == user.id)
            .where(Task.is_archived == false())
            .where(
                or_(
                    func.greatest(UsersCategories.updated_at, Task.updated_at) > after_datetime,
                    and_(
                        func.greatest(UsersCategories.updated_at, Task.updated_at) == after_datetime, Task.id > after_id
                    ),
                )
            )
            .order_by(func.greatest(UsersCategories.updated_at, Task.updated_at), Task.id)
            .limit(limit)
        )
        print("\n******\n", select_statement, "\n******\n")
        tasks = await self._session.execute(select_statement)
        return tasks.all()

    async def count_user_tasks_actualized_after(self, user: User, after_datetime: datetime, after_id: int) -> int:
        """Возвращает количество заданий, доступных пользователю user и актуализированных
        после заданного момента времени after_datetime.
        За время актуализации задачи принимается наибольшее из времён: изменения задачи и назначения
        заданному пользователю категории, к которой относится задача.
        Задачи, время актуализации которых совпадает с заданным, но их id > after_id, также
        принимаются в расчёт.
        """
        select_statement = (
            select(func.count(Task.id))
            .join(Category)
            .join(UsersCategories)
            .where(UsersCategories.user_id == user.id)
            .where(Task.is_archived == false())
            .where(
                or_(
                    func.greatest(UsersCategories.updated_at, Task.updated_at) > after_datetime,
                    and_(
                        func.greatest(UsersCategories.updated_at, Task.updated_at) == after_datetime, Task.id > after_id
                    ),
                )
            )
        )
        print("\n******\n", select_statement, "\n******\n")
        count = await self._session.scalar(select_statement)
        return count

    async def get_all_user_tasks(self) -> Sequence[Task]:
        """Получить список задач из категорий на которые подписан пользователь."""
        all_tasks = await self._session.scalars(select(Task).options(joinedload(Task.category)))
        return all_tasks.all()

    async def get_tasks_limit_for_user(self, limit: int, offset: int, user: User) -> Sequence[Task]:
        """Получить limit-выборку из списка всех задач пользователя."""
        task_limit_for_user = await self._session.scalars(
            (
                select(Task)
                .join(Category)
                .options(joinedload(Task.category))
                .where(Category.users.any(id=user.id))
                .where(Task.is_archived == false())
                .limit(limit)
                .offset(offset)
            )
        )

        return task_limit_for_user.all()

    async def get_user_tasks_count(self, user: User) -> int:
        """Получить общее количество задач для пользователя."""
        return await self._session.scalar(
            select(func.count(Task.id))
            .join(Category)
            .where(Category.users.any(id=user.id))
            .where(Task.is_archived == false())
        )

    async def get_user_task_id(self, task_id) -> Optional[Task]:
        """Получить задачу по id с привязанными полями категории."""
        return await self._session.scalar(select(Task).options(joinedload(Task.category)).where(Task.id == task_id))

    async def get_user_tasks_ids(self, ids: list[int]) -> Sequence[Task]:
        """Получить список задач по ids c привязанными полями категорий."""
        tasks = await self._session.scalars(select(Task).options(joinedload(Task.category)).where(Task.id.in_(ids)))
        return tasks.all()

    async def archive(self, id: int) -> None:
        instance = await self.get(id, is_archived=False)
        instance.is_archived = True
        await self.update(instance.id, instance)
