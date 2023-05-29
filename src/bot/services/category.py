import contextlib
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Category
from src.core.db.repository.category import CategoryRepository


class CategoryService:
    """Сервис бота для работы с моделью Category."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session):
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def get_unarchived_parents(self) -> list[Category]:
        async with self._sessionmaker() as session:
            repository = CategoryRepository(session)
            return await repository.get_unarchived_parents()

    async def get_unarchived_subcategories(self, parent_id) -> list[Category]:
        async with self._sessionmaker() as session:
            repository = CategoryRepository(session)
            return await repository.get_unarchived_subcategories(parent_id)
