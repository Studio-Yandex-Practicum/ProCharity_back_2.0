import math
from typing import Any, Generic, TypeVar

from src.core.db.models import User
from src.core.db.repository import AbstractRepository, UserRepository
from src.core.db.repository.base import FilterableRepository

DatabaseModel = TypeVar("DatabaseModel")


class BasePaginator(Generic[DatabaseModel]):
    """Базовый класс для пагинации."""

    def __init__(
        self,
        repository: AbstractRepository[DatabaseModel],
    ) -> None:
        self.repository = repository

    def _get_paginated_dict(
        self, total_objects_count, objects: list[DatabaseModel], page: int, limit: int, url: str
    ) -> dict:
        pages = math.ceil(total_objects_count / limit)
        next_page = page + 1 if page < pages else None
        previous_page = page - 1 if page > 1 else None
        next_url = f"{url}?page={next_page}&limit={limit}" if next_page else None
        previous_url = f"{url}?page={previous_page}&limit={limit}" if previous_page else None

        return {
            "total": total_objects_count,
            "pages": pages,
            "current_page": page,
            "next_page": next_page,
            "previous_page": previous_page,
            "next_url": next_url,
            "previous_url": previous_url,
            "result": objects,
        }

    async def paginate(self, objects: list[DatabaseModel], page: int, limit: int, url: str) -> dict:
        total_objects_count = await self.repository.count_all()
        return self._get_paginated_dict(total_objects_count, objects, page, limit, url)


class FilterablePaginator(BasePaginator, Generic[DatabaseModel]):
    """Класс для пагинации с фильтрацией."""

    def __init__(self, repository: FilterableRepository) -> None:
        super().__init__(repository)

    async def paginate(
        self, objects: list[DatabaseModel], page: int, limit: int, url: str, filter_by: dict[str:Any]
    ) -> dict:
        total_objects_count = await self.repository.count_by_filter(filter_by)
        return self._get_paginated_dict(total_objects_count, objects, page, limit, url)


class UserPaginator(FilterablePaginator[User]):
    """Класс для пагинации и фильтрации данных из модели User."""

    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(user_repository)
