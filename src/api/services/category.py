from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import ContentService
from src.core.db import get_session
from src.core.db.repository.category import CategoryRepository


class CategoryService(ContentService):
    """Сервис для работы с моделью Category."""

    def __init__(
            self, category_repository: CategoryRepository = Depends(), session: AsyncSession = Depends(get_session)
    ) -> None:
        super().__init__(category_repository, session)
