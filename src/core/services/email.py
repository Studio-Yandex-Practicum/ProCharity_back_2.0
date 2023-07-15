import contextlib
from typing import Any, Generator

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.db.db import get_session
from src.core.db.repository.user import UserRepository
from src.core.exceptions import exceptions
from src.settings import settings


class EmailSchema(BaseModel):
    recipients: list[EmailStr]
    template_body: dict[str, Any] | None


class EmailProvider:
    """Класс для отправки электронных писем."""

    def __init__(self, sessionmaker: Generator[AsyncSession, None, None] = get_session):
        conf = ConnectionConfig(
            MAIL_USERNAME=settings.MAIL_LOGIN,
            MAIL_PASSWORD=settings.MAIL_PASSWORD,
            MAIL_FROM=settings.ORGANIZATIONS_EMAIL,
            MAIL_PORT=settings.MAIL_PORT,
            MAIL_SERVER=settings.MAIL_SERVER,
            MAIL_FROM_NAME="ProCharity Bot",
            MAIL_STARTTLS=settings.MAIL_STARTTLS,
            MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
            USE_CREDENTIALS=settings.USE_CREDENTIALS,
            VALIDATE_CERTS=settings.VALIDATE_CERTS,
        )
        self.fastmail = FastMail(conf)
        self._sessionmaker = contextlib.asynccontextmanager(sessionmaker)

    async def __send_mail(
        self,
        email_obj: EmailSchema,
        subject: str,
        template_name: str | None,
        body: str | None,
    ) -> None:
        """Базовый метод отправки сообщения на электронную почту.
        Аргументы:
            recipients (list[EmailStr]): список email получателей
            subject (str): тема сообщения
            template_body (dict[str, Any]): значения переменных для шаблона сообщения
            template_name (str): название шаблона для сообщения
            body (str): тело электронного письма
        """
        message = MessageSchema(
            subject=subject,
            recipients=email_obj.recipients,
            template_body=email_obj.template_body,
            body=body,
            subtype=MessageType.html,
        )

        try:
            await self.fastmail.send_message(message, template_name)
        except Exception as exc:
            raise exceptions.EmailSendError(email_obj.recipients, exc)

    async def send_question_feedback(self, telegram_id: int, message: str, email: list[EmailStr]) -> None:
        """Отправляет email на почтовый ящик администратора с отзывом/вопросом."""
        recipients = email
        email_obj = EmailSchema(recipients=recipients, template_body=None)
        try:
            async with self._sessionmaker() as session:
                user_repository = UserRepository(session)
                user = await user_repository.get_by_telegram_id(telegram_id)
        except ValueError:
            user = None
        if user.email is None:
            user.email = "пользователь не указал свой email"
        await self.__send_mail(
            email_obj,
            subject=f"Сообщение от пользователя {user.username}(email: {user.email})",
            body=message,
            template_name=None,
        )
