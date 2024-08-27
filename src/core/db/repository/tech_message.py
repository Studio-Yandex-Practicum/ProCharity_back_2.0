from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import TechMessage
from src.core.db.repository.base import ArchivableRepository


class TechMessageRepository(ArchivableRepository):
    """Репозиторий для работы с моделью TechMessage."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, TechMessage)
