from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import not_, and_, select

from src.core.db.db import get_session
from src.core.db.models import Category
from src.core.db.repository.base import ContentRepository


class CategoryRepository(ContentRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Category)

    async def get_unarchived_parents(self) -> list[Category]:
        categories = await self._session.execute(
            select(Category).where(and_(not_(Category.archive)), Category.parent_id.is_(None))
        )
        return categories.scalars().all()

    async def get_unarchived_subcategories(self, parent_id: int) -> list[Category]:
        categories = await self._session.execute(
            select(Category).where(and_(not_(Category.archive)), Category.parent_id == parent_id)
        )
        return categories.scalars().all()
