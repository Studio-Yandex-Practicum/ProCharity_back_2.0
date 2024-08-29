from typing import Sequence

from sqlalchemy import false, func, null, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Category, User
from src.core.db.repository.base import ContentRepository


class CategoryRepository(ContentRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Category)

    async def get_unarchived_subcategories(self, parent_id: int) -> Sequence[Category]:
        unarchived_subcategories = await self._session.scalars(
            select(Category).where(Category.is_archived == false()).where(Category.parent_id == parent_id)
        )
        return unarchived_subcategories.all()

    async def get_unarchived_parents_with_children_count(self):
        parent_and_children_count_subquery = (
            select(Category.parent_id, func.count(Category.id).label("children_count"))
            .where(Category.is_archived == false())
            .where(Category.parent_id != null())
            .group_by(Category.parent_id)
            .subquery()
        )
        parents_with_children_count = await self._session.execute(
            select(Category.name, Category.id, parent_and_children_count_subquery.c.children_count)
            .select_from(Category)
            .join(parent_and_children_count_subquery, Category.id == parent_and_children_count_subquery.c.parent_id)
            .order_by(Category.name)
        )
        return parents_with_children_count.all()

    async def get_user_categories(self, user: User, is_archived: bool | None = False) -> Sequence[Category]:
        """Возвращает список категорий пользователя."""
        statement = select(Category).join(User.categories).where(User.id == user.id)
        user_categories = await self._session.scalars(self._add_archiveness_test_to_select(statement, is_archived))
        return user_categories.all()
