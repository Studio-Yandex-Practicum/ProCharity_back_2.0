from typing import Any

from src.core.db.models import TechMessage
from src.core.db.repository import TechMessageRepository


class TechMessageService:
    """Сервис технических сообщений для админов бота."""

    def __init__(self, repository: TechMessageRepository):
        self._repository: TechMessageRepository = repository

    async def create(self, message: str) -> TechMessage:
        return await self._repository.create(TechMessage(text=message))

    async def get_filtered_tech_messages_by_page(self, filter_by: dict[str:Any], page: int, limit: int) -> dict:
        return await self._repository.get_filtered_tech_messages_by_page(filter_by, page, limit)

    async def get(self, id: int) -> TechMessage:
        return await self._repository.get(id)

    async def partial_update(self, id: int, data: dict) -> TechMessage:
        return await self._repository.partial_update(id, data)

    async def archive(self, id: int) -> None:
        await self._repository.archive(id)
