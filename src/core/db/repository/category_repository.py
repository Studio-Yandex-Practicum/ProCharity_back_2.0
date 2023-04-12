from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Category
from src.core.db.repository.base import AbstractRepository


class CategoryRepository(AbstractRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Category)

    async def create_all(self, new_categories: list[Category]) -> None:
        """Создает несколько категорий в базе данных."""
        for category in new_categories:
            self._session.add(category)
        await self._session.commit()

    async def archive_categories(self, categories_to_archive_id: list[UUID]) -> None:
        """Добавляет несколько категорий в архив."""
        for id in categories_to_archive_id:
            category_to_archive = await self.get(id)
            category_to_archive.archive = True
        await self._session.commit()

    async def get_unarchive_categories_id(self) -> list[UUID]:
        """Получает из базы id всех незаархивированных категорий."""
        unarchive_categories_id = await self._session.execute(select(Category.id).where(not Category.archive))
        return unarchive_categories_id.scalars().all()
