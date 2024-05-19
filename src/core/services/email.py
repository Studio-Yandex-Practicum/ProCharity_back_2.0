from typing import Any

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import async_sessionmaker
from structlog import get_logger

from src.settings import Settings

logger = get_logger()


class EmailSchema(BaseModel):
    recipients: list[EmailStr]
    template_body: dict[str, Any] | None


class EmailProvider:
    """Класс для отправки электронных писем."""

    def __init__(self, sessionmaker: async_sessionmaker, settings: Settings):
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
        self._sessionmaker = sessionmaker
        self._settings = settings

    async def __send_mail(
        self,
        email_obj: EmailSchema,
        subject: str,
        template_name: str | None,
        body: str | None = None,
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

        await self.fastmail.send_message(message, template_name)

    async def send_question(
        self,
        telegram_link: str | None,
        name: str,
        to_email: EmailStr,
        external_id: str | None = None,
        from_email: EmailStr | None = None,
        message: str = "",
    ) -> None:
        """Отправляет указанным адресатам вопросы от волонтера.
        Args:
            id (int): id волонтера
            telegram_id (int): telegram_id волонтера
            name (str): Имя волонтера
            message (str): Текст вопроса
            email (EmailStr | list[EmailStr]): email получателя/получателей
        """
        template_body = {
            "id": external_id,
            "telegram_link": telegram_link,
            "name": name,
            "message": message,
            "email": from_email,
        }
        recipients = [to_email]
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        try:
            await self.__send_mail(
                email_obj, subject="Вопрос от волонтера'", template_name="send_question.html", body=None
            )
        except Exception as e:
            logger.exception(e)

    def create_temp_body(self, path: str, token: str) -> dict:
        """Создает тело шаблона со ссылкой с токеном для отправки
        пригласительной ссылки или сброса пароля.
        Args:
            path (str): маршрут ссылки
            token (str): секретный токен
        """
        token_expiration = self._settings.TOKEN_EXPIRATION
        template_body = {
            "link": f"{self._settings.APPLICATION_URL}admin/#/{path}/{token}",
            "expiration": token_expiration,
            "token": token,
        }
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

    async def unsubscribe_notification(
        self, user_name: str, user_id: str, reason: str, to_email: EmailStr | list[EmailStr]
    ) -> None:
        """Отправляет уведомление с причиной отписки пользователя.

        Args:
            user_name (str): Имя пользователя.
            user_id (str): Идентификатор пользователя.
            reason (str): Указанная причина отписки.
            to_email (EmailStr | list[EmailStr]): email получателя/получателей
        """
        template_body = {"user_name": user_name, "user_id": user_id, "reason": reason}
        recipients = [to_email]
        email_obj = EmailSchema(recipients=recipients, template_body=template_body)
        try:
            await self.__send_mail(
                email_obj,
                subject="Уведомление об отписке пользователя",
                template_name="unsubscribe_notification.html",
                body=None,
            )
            logger.info(f"Уведомление об отписке {user_name} отправлено на {to_email}")
        except Exception as e:
            logger.exception(e)
