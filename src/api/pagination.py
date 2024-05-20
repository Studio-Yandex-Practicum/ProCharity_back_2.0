import math
from typing import Generic, TypeVar

from src.core.db.models import User
from src.core.db.repository import AbstractRepository, UserRepository

DatabaseModel = TypeVar("DatabaseModel")


class BasePaginator(Generic[DatabaseModel]):
    """Базовый класс для пагинации."""

    def __init__(
        self,
        repository: AbstractRepository[DatabaseModel],
    ) -> None:
        self.repository = repository

    async def paginate(self, objects: list[DatabaseModel], page: int, limit: int, url: str) -> dict:
        count_objects = await self.repository.count_all()

        pages = math.ceil(count_objects / limit)
        next_page = page + 1 if page < pages else None
        previous_page = page - 1 if page > 1 else None
        next_url = f"{url}?page={next_page}&limit={limit}" if next_page else None
        previous_url = f"{url}?page={previous_page}&limit={limit}" if previous_page else None

        return {
            "total": count_objects,
            "pages": pages,
            "current_page": page,
            "next_page": next_page,
            "previous_page": previous_page,
            "next_url": next_url,
            "previous_url": previous_url,
            "result": objects,
        }


class UserPaginator(BasePaginator[User]):
    """Класс для пагинации данных из модели User."""

    def __init__(self, user_repository: UserRepository) -> None:
        super().__init__(user_repository)
