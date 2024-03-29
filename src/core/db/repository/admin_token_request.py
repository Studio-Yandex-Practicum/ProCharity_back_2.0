from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.models import AdminTokenRequest
from src.core.db.repository.base import AbstractRepository


class AdminTokenRequestRepository(AbstractRepository):
    """Репозиторий для работы с моделью AdminTokenRequest."""

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AdminTokenRequest)

    async def get_by_token(self, token: str) -> AdminTokenRequest | None:
        """Возвращает пользователя (или None) по invitation token."""
        return await self._session.scalar(select(AdminTokenRequest).where(AdminTokenRequest.token == token))

    async def create_invitation_token(self, email: str, token: str, token_expiration_date: datetime) -> None:
        """При отсутствии записи в БД создает пользователя с созданным токеном."""
        record = AdminTokenRequest.query.filter_by(email=email).first()
        if record:
            record.token = token
            record.token_expiration_date = token_expiration_date
            await self.session.commit()
        else:
            user = AdminTokenRequest(email=email, token=token, token_expiration_date=token_expiration_date)
            await self.session.add(user)
            await self.session.commit()
