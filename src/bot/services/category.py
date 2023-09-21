from src.core.db.models import Category
from src.core.db.repository.category import CategoryRepository


class CategoryService:
    """Сервис бота для работы с моделью Category."""

    def __init__(self, category_repository: CategoryRepository) -> None:
        self._category_repository = category_repository

    async def get_unarchived_parents(self) -> list[Category]:
        return await self._category_repository.get_unarchived_parents()

    async def get_unarchived_subcategories(self, parent_id) -> list[Category]:
        async with self._sessionmaker() as session:
            repository = CategoryRepository(session)
            return await repository.get_unarchived_subcategories(parent_id)

    async def get_unarchived_parents_with_children_count(self) -> dict[Category, int]:
        async with self._sessionmaker() as session:
            repository = CategoryRepository(session)
            categories = await repository.get_unarchived_parents()
            result = {}
            for category in categories:
                children = await repository.get_unarchived_subcategories(category.id)
                result[category] = len(children.all())
            return result
