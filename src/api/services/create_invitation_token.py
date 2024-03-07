import contextlib
import uuid
from datetime import datetime, timedelta
from typing import Generator

from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.models import AdminTokenRequest
from src.settings import settings


async def create_invitation_token(
    email: EmailStr | list[EmailStr], sessionmaker: Generator[AsyncSession, None, None] = get_session
) -> str:
    """Создает токен для отправки пригласительной ссылки или сброса пароля.
    Args:
        email (EmailStr | list[EmailStr]): email получателя
        sessionmaker (Generator[AsyncSession, None, None]): мейкер сессий
    """
    _sessionmaker = contextlib.asynccontextmanager(sessionmaker)
    token_expiration = settings.TOKEN_EXPIRATION
    token_expiration_date = datetime.now() + timedelta(hours=token_expiration)
    token = str(uuid.uuid4())

    record = AdminTokenRequest.query.filter_by(email=email).first()
    async with _sessionmaker() as session:
        if record:
            record.token = token
            record.token_expiration_date = token_expiration_date
            await session.commit()
        else:
            user = AdminTokenRequest(email=email, token=token, token_expiration_date=token_expiration_date)
            await session.add(user)
            await session.commit()
        return token
