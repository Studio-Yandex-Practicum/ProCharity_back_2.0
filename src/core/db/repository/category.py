from sqlalchemy import false, func, null, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Category
from src.core.db.repository.base import ContentRepository


class CategoryRepository(ContentRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Category)

    async def get_unarchived_subcategories(self, parent_id: int) -> list[Category]:
        return await self._session.scalars(
            select(Category).where(Category.is_archived == false()).where(Category.parent_id == parent_id)
        )

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
        )
        return parents_with_children_count.all()
