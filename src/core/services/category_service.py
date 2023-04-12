from src.core.db.repository.category_repository import CategoryRepository
from fastapi import Depends
from src.core.db.models import Category
from src.api.schemas import CaregoryRequest


class CategoryService:
    def __init__(self, category_repository: CategoryRepository = Depends()):
        self.__category_repository = category_repository

    async def actualize_categories(self, new_categories_request: list[CaregoryRequest]) -> Category:
        new_categories = []
        for category in new_categories_request:
            new_category_data = category.dict()
            new_category_data['archive'] = False
            new_category = Category(**new_category_data)
            new_categories.append(new_category)

        new_categories_dict = {category.id: category for category in new_categories}
        categories_db = await self.__category_repository.get_all()
        categories_id_db = [category.id for category in categories_db]
        unarchive_categories_id_db = await self.__category_repository.get_unarchive_categories_id()
        categories_db_dict = {category.id: category for category in categories_db}

        categories_to_add = []
        categories_to_update = []
        categories_to_archive_id = []

        for category in new_categories:
            if category.id not in categories_id_db:
                categories_to_add.append(category)
            elif (
                categories_db_dict[category.id].name != category.name
                or categories_db_dict[category.id].parent_id != category.parent_id
                or categories_db_dict[category.id].archive != category.archive
            ):
                categories_to_update.append(category)

        for id in unarchive_categories_id_db:
            if not new_categories_dict.get(id):
                categories_to_archive_id.append(id)

        if categories_to_add:
            await self.__category_repository.create_all(categories_to_add)
        if categories_to_update:
            for category_to_update in categories_to_update:
                category = await self.__category_repository.get(category_to_update.id)
                category.name = category_to_update.name
                category.parent_id = category_to_update.parent_id
                category.archive = category_to_update.archive
                await self.__category_repository.update(category.id, category)
        if categories_to_archive_id:
            await self.__category_repository.archive_categories(categories_to_archive_id)

    async def get_all_categories(self) -> list[Category]:
        categories = await self.__category_repository.get_all()
        return categories
