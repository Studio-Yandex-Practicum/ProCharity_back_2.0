from fastapi import Depends
from sqlalchemy import false, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import case

from src.core.db.db import get_session
from src.core.db.models import Category
from src.core.db.repository.base import AbstractRepository


class CategoryRepository(AbstractRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Category)

    async def get_unarchive_categories_id(self) -> list[int]:
        """Получает из базы id всех не заархивированных категорий."""
        unarchive_categories_id = await self._session.execute(select(Category.id).where(Category.archive == false()))
        return unarchive_categories_id.scalars().all()

    async def update_all_categories(self, categories_to_update: list[Category]) -> None:
        """Обновляет несколько категорий."""
        names, parent_ids, archives = [], [], []
        for category_to_update in categories_to_update:
            names.append((Category.id == category_to_update.id, category_to_update.name))
            parent_ids.append((Category.id == category_to_update.id, category_to_update.parent_id))
            archives.append((Category.id == category_to_update.id, category_to_update.archive))
        statement = update(Category).values(
            name=case(*names, else_=Category.name),
            parent_id=case(*parent_ids, else_=Category.parent_id),
            archive=case(*archives, else_=Category.archive),
        )
        await self._session.execute(statement)
        await self._session.commit()

    async def archive_categories(self, categories: list[int]) -> None:
        """Добавляет несколько категорий в архив."""
        await self._session.execute(
            update(Category).where(Category.id.in_(categories)).values({"archive": True})
        )
        await self._session.commit()
