from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from pydantic import BaseModel, EmailStr

from src.core.exceptions import exceptions
from src.settings import settings


class EmailSchema(BaseModel):
    email: list[EmailStr]


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


async def send_question_feedback(telegram_id: int, message: str, email: list[EmailStr]) -> None:
    """Отправляет email на почтовый ящик администратора с отзывом/паролем."""
    message = MessageSchema(
        subject=f"Сообщение от пользователя c telegram_id = {telegram_id}",
        recipients=email,
        body=message,
        subtype=MessageType.html,
    )
    fastmail = FastMail(conf)
    try:
        await fastmail.send_message(message)
    except Exception as exc:
        raise exceptions.EmailSendError(email, exc)
