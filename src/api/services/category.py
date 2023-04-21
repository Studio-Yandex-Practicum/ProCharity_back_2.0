from fastapi import Depends

from src.api.schemas import CaregoryRequest
from src.core.db.models import Category
from src.core.db.repository.category import CategoryRepository


class CategoryService:
    """Сервис для работы с моделью Category."""

    def __init__(self, category_repository: CategoryRepository = Depends()):
        self.__category_repository = category_repository

    async def actualize_categories(self, categories: list[CaregoryRequest]) -> None:
        to_create, to_update = [], []
        await self.__category_repository.archive_all()
        already_have = await self.__category_repository.get_all_ids()
        for category in categories:
            if category.id not in already_have:
                to_create.append(Category(**category.dict(), archive=False))
            else:
                category_dict = category.dict()
                category_dict['archive'] = False
                to_update.append(category_dict)
        if to_create:
            await self.__category_repository.create_all(to_create)
        if to_update:
            await self.__category_repository.update_all(to_update)

    async def get_all_categories(self) -> list[Category]:
        categories = await self.__category_repository.get_all()
        return categories
