from src.core.db.repository import UserRepository
from src.core.pagination import BasePaginator


class UserPaginator(BasePaginator):
    """Класс для пагинации данных из модели User."""

    def __init__(self, user_repository: UserRepository) -> None:
        self.repository = user_repository
