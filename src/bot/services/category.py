from src.core.db.models import Category
from src.core.db.repository.category import CategoryRepository


class CategoryService:
    """Сервис бота для работы с моделью Category."""

    def __init__(self, category_repository: CategoryRepository) -> None:
        self._category_repository = category_repository

    async def get(self, id: int, *, is_archived: bool | None = False) -> Category:
        return await self._category_repository.get(id, is_archived=is_archived)

    async def get_unarchived_subcategories(self, parent_id) -> list[Category]:
        return await self._category_repository.get_unarchived_subcategories(parent_id)

    async def get_unarchived_parents_with_children_count(self):  # -> dict[Category, int]:
        return await self._category_repository.get_unarchived_parents_with_children_count()
