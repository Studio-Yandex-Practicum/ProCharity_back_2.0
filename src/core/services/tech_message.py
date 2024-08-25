from src.core.db.models import TechMessage
from src.core.db.repository import TechMessageRepository


class TechMessageService:
    """Сервис технических сообщений для админов бота."""

    def __init__(self, repository: TechMessageRepository):
        self._repository: TechMessageRepository = repository

    async def create(self, message: str) -> TechMessage:
        return await self._repository.create(TechMessage(text=message))
