import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from sqlalchemy import select
from structlog import get_logger

from src.core.db import get_session
from src.core.db.models import AdminTokenRequest, AdminUser
from src.core.services.email import EmailProvider
from src.settings import settings

logger = get_logger()


async def create_token_for_super_user() -> None:
    """Создаёт токен и отправляет его на почту администратора"""
    session_manager = asynccontextmanager(get_session)
    async with session_manager() as session:
        admin = await session.scalar(select(AdminUser).where(AdminUser.email == settings.EMAIL_ADMIN))

        if admin is None:
            token = str(uuid.uuid4())
            token_expiration_date = datetime.now() + timedelta(seconds=settings.TOKEN_EXPIRATION)
            admin_token = AdminTokenRequest(
                email=settings.EMAIL_ADMIN, is_superuser=True, token=token, token_expiration_date=token_expiration_date
            )

            session.add(admin_token)
            await session.commit()

            email_provider = EmailProvider(session, settings)
            await email_provider.send_invitation_link(settings.EMAIL_ADMIN, token)

            await logger.ainfo(
                f'Super user registration: The invitation "{token}" generated for {settings.EMAIL_ADMIN}.'
            )
