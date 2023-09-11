from src.core.db.models import Category
from src.core.db.repository.category import CategoryRepository


class CategoryService:
    """Сервис бота для работы с моделью Category."""

    def __init__(self, category_repository: CategoryRepository):
        self._category_repository = category_repository

    async def get_unarchived_parents(self) -> list[Category]:
        return await self._category_repository.get_unarchived_parents()

    async def get_unarchived_subcategories(self, parent_id) -> list[Category]:
        return await self._category_repository.get_unarchived_subcategories(parent_id)
