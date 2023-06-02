
from fastapi import Depends
from sqlalchemy import and_, not_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Category
from src.core.db.repository.base import ContentRepository


class CategoryRepository(ContentRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Category)

    async def get_unarchived_parents(self) -> list[Category]:
        categories = await self._session.scalars(
            select(Category)
            .where(Category.is_archived == False)
            .where(Category.parent_id == None) # noqa
        )
        return categories

    async def get_unarchived_subcategories(self, parent_id: int) -> list[Category]:
        categories = await self._session.scalars(
            select(Category).where(Category.is_archived == False).where(Category.parent_id == parent_id))
        return categories
