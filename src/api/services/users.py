import math

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.services.base import ContentService
from src.api.utils import user_formatter, users_paginate_responce
from src.core.db.models import User
from src.core.db.repository import UserRepository


class UserService(ContentService):
    """Сервис для работы с моделью User."""

    def __init__(
        self,
        user_repository: UserRepository,
        session: AsyncSession,
    ) -> None:
        self._user_repository: UserRepository = user_repository
        self._session: AsyncSession = session

    async def get_by_user_id(self, user_id: int) -> User | None:
        return await self._user_repository.get_by_user_id(user_id)

    async def get_users_by_page(self, page: int, limit: int) -> dict:
        offset = (page - 1) * limit
        users = await self._user_repository.get_users_by_page(limit, offset)
        count_users = await self._user_repository.get_count_all_users()

        result = []
        for user in users:
            result.append(user_formatter(user))

        pages = math.ceil(count_users / limit) if count_users else None
        next_page = page + 1 if page != pages else None
        previous_page = page - 1 if page != 1 else None
        next_url = f"/api/users/?page={next_page}&limit={limit}" if next_page else None
        previous_url = f"/api/users/?page={previous_page}&limit={limit}" if previous_page else None

        pagination_data = {
            "total": count_users,
            "pages": pages,
            "current_page": page,
            "next_page": next_page,
            "previous_page": previous_page,
            "next_url": next_url,
            "previous_url": previous_url,
            "result": result,
        }

        return users_paginate_responce(pagination_data)
