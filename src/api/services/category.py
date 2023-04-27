from fastapi import Depends

from src.api.schemas import CaregoryRequest
from src.api.services.base import ContentService
from src.core.db.models import Category
from src.core.db.repository.category import CategoryRepository


class CategoryService(ContentService):
    """Сервис для работы с моделью Category."""

    def __init__(self, category_repository: CategoryRepository = Depends()):
        super().__init__(category_repository)

    async def actualize_categories(self, categories: list[CaregoryRequest]) -> None:
        await self.actualize_objects(categories, Category)

    async def get_all_categories(self) -> list[Category]:
        return await self.get_all_objects()
