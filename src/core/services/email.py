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
    recipients: EmailStr | list[EmailStr]
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
            TEMPLATE_FOLDER=settings.EMAIL_TEMPLATE_DIRECTORY,
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
        Args:
            email_obj (EmailSchema): объект письма
            subject (str): тема сообщения
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

    async def send_question_feedback(self, telegram_id: int, message: str, email: EmailStr | list[EmailStr]) -> None:
        """Отправляет email на почтовый ящик администратора с отзывом/вопросом.
        Args:
            telegram_id (int): telegram_id волонтера
            message (str): текст сообщения
            email (EmailStr | list[EmailStr]): email получателя
        """
        if isinstance(email, str):
            recipients = [email]
        elif isinstance(email, list):
            recipients = email
        else:
            raise ValueError("Invalid email format")
        email_obj = EmailSchema(recipients=recipients, template_body=None)
        async with self._sessionmaker() as session:
            user_repository = UserRepository(session)
            user = await user_repository.get_by_telegram_id(telegram_id)
        await self.__send_mail(
            email_obj,
            subject=(
                f"Сообщение от пользователя {user.first_name} ({user.email or 'пользователь не указал свой email'})"
            ),
            body=message,
            template_name=None,
        )

    async def send_question(
        self, id: int, telegram_id: int, name: str, message: str, email: EmailStr | list[EmailStr]
    ) -> None:
        """Отправляет указанным адресатам вопросы от волонтера.
        Args:
            id (int): id волонтера
            telegram_id (int): telegram_id волонтера
            name (str): name волонтера
            message (str): текст вопроса
            email (EmailStr | list[EmailStr]): email получателя
        """
        template_body = {"id": id, "telegram_id": telegram_id, "name": name, "message": message}
        recipients = [email]
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        await self.__send_mail(email_obj, subject="Вопрос от волонтера'", template_name="send_question.html", body=None)

    async def create_temp_body(self, path: str, token: str) -> dict:
        """Создает тело шаблона со ссылкой с токеном для отправки
        пригласительной ссылки или сброса пароля.
        Args:
            path (str): маршрут ссылки
            token (str): секретный токен
        """
        token_expiration = settings.TOKEN_EXPIRATION
        template_body = {"link": f"{settings.HOST_NAME}/#/{path}/{token}", "expiration": token_expiration}
        return template_body

    async def send_invitation_link(self, email: str, token: str) -> None:
        """Отправляет указанным адресатам ссылку для регистрации в проекте.
        Args:
            email (str): email получателя
            token (str): секретный токен
        """
        template_body = self.create_temp_body("invitation_link", token)
        recipients = [email]
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        await self.__send_mail(
            email_obj, subject="Приглашение в проект 'ProCharity'", template_name="invitation_email.html", body=None
        )

    async def send_restore_password_link(self, email: str, token: str) -> None:
        """Отправляет email на почтовый ящик со ссылкой на сброс пароля.
        Args:
            email (str): email получателя
            token (str): секретный токен
        """
        template_body = self.create_temp_body("reset_password", token)
        recipients = [email]
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        await self.__send_mail(
            email_obj,
            subject="Восстановленный пароль от учетной записи в проекте 'ProCharity'",
            template_name="password_reset.html",
            body=None,
        )
