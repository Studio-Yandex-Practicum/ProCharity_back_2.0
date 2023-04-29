from fastapi import Depends

from src.api.services.base import ContentService
from src.core.db.repository.category import CategoryRepository


class CategoryService(ContentService):
    """Сервис для работы с моделью Category."""

    def __init__(self, category_repository: CategoryRepository = Depends()):
        super().__init__(category_repository)
