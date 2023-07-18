from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import ExternalSiteUser
from src.core.db.repository.base import AbstractRepository


class ExternalSiteUserRepository(AbstractRepository):
    """Репозиторий для работы с моделью ExternalSiteUser."""

    def __init__(self, session: AsyncSession = Depends(get_session)) -> None:
        super().__init__(session, ExternalSiteUser)
