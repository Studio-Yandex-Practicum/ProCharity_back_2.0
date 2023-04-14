from fastapi import Depends

from src.api.schemas import CaregoryRequest
from src.core.db.models import Category
from src.core.db.repository.category_repository import CategoryRepository


class CategoryService:
    """Сервис для работы с моделью Category."""

    def __init__(self, category_repository: CategoryRepository = Depends()):
        self.__category_repository = category_repository

    async def actualize_categories(self, categories: list[CaregoryRequest]) -> None:
        async def get_categories_to_add_or_update(new_categories, categories_db_dict):
            categories_to_add = []
            categories_to_update = []
            for category in new_categories:
                if category.id not in categories_id_db:
                    categories_to_add.append(category)
                elif (
                    categories_db_dict[category.id].name != category.name
                    or categories_db_dict[category.id].parent_id != category.parent_id
                    or categories_db_dict[category.id].archive != category.archive
                ):
                    categories_to_update.append(category)
            return (categories_to_add, categories_to_update)

        async def get_categories_to_archive_id(unarchive_categories_id_db):
            categories_to_archive_id = []
            for idx in unarchive_categories_id_db:
                if not new_categories_dict.get(idx):
                    categories_to_archive_id.append(idx)
            return categories_to_archive_id

        new_categories = []
        for category in categories:
            new_categories.append(Category(**category.dict(), archive=False))

        new_categories_dict = {category.id: category for category in new_categories}
        categories_db = await self.__category_repository.get_all()
        categories_id_db = [category.id for category in categories_db]
        unarchive_categories_id_db = await self.__category_repository.get_unarchive_categories_id()
        categories_db_dict = {category.id: category for category in categories_db}

        categories_to_add, categories_to_update = await get_categories_to_add_or_update(
            new_categories, categories_db_dict
        )
        categories_to_archive_id = await get_categories_to_archive_id(unarchive_categories_id_db)
        await self.add_categories(categories_to_add)
        await self.update_categories(categories_to_update)
        await self.archive_categories(categories_to_archive_id)

    async def add_categories(self, categories_to_add):
        if categories_to_add:
            await self.__category_repository.create_all(categories_to_add)

    async def update_categories(self, categories_to_update):
        if categories_to_update:
            await self.__category_repository.update_all_categories(categories_to_update)

    async def archive_categories(self, categories_to_archive_id):
        if categories_to_archive_id:
            await self.__category_repository.archive_categories(categories_to_archive_id)

    async def get_all_categories(self) -> list[Category]:
        categories = await self.__category_repository.get_all()
        return categories
