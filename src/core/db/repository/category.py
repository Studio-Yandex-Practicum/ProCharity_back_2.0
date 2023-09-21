from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import Category
from src.core.db.repository.base import ContentRepository


class CategoryRepository(ContentRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Category)

    async def get_unarchived_parents(self) -> list[Category]:
        categories = await self._session.scalars(
            select(Category).where(Category.is_archived == False).where(Category.parent_id == None)  # noqa
        )
        return categories

    async def get_unarchived_subcategories(self, parent_id: int) -> list[Category]:
        categories = await self._session.scalars(
            select(Category).where(Category.is_archived == False).where(Category.parent_id == parent_id)  # noqa
        )
        return categories

    async def get_unarchived_parents_with_children_count(self):
        subq = (
            select(Category.parent_id, func.count(Category.id).label("children_count"))
            .where(Category.is_archived == False)  # noqa
            .where(Category.parent_id != None)  # noqa
            .group_by(Category.parent_id)
            .subquery()
        )
        parents_with_children_count = await self._session.execute(
            select(Category.name, Category.id, subq.c.children_count)
            .select_from(Category)
            .join(subq, Category.id == subq.c.parent_id)
        )
        return parents_with_children_count.all()
