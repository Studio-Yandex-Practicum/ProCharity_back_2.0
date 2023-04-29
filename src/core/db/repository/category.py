from fastapi import Depends
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import Category
from src.core.db.repository.base import AbstractRepository
from src.core.utils import auto_commit


class CategoryRepository(AbstractRepository):
    """Репозиторий для работы с моделью Category."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, Category)

    @auto_commit
    async def archive_all(self, commit=True) -> None:
        """Добавляет все категории в архив."""
        await self._session.execute(update(Category).values({"archive": True}))
