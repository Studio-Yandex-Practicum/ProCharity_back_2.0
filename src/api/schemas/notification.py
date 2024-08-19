from pydantic import BaseModel, Field

from src.api.schemas.base import RequestBase
from src.core.enums import TelegramNotificationUsersGroups


class TelegramNotificationRequest(RequestBase):
    """
    Класс формирования параметров запроса для отправки
    сообщения определенному пользователю.
    """

    message: str = Field(..., min_length=1)


class TelegramNotificationUsersRequest(TelegramNotificationRequest):
    """Класс формирования параметров запроса для отправки
    сообщения определенной группе пользователей."""

    has_mailing: TelegramNotificationUsersGroups


class Message(TelegramNotificationRequest):
    id_hash: str


class MessageList(RequestBase):
    messages: list[Message]


class ErrorsSending(BaseModel):
    """
    Класс для вывода ошибок при отправке сообщения.
    """

    type: str = "TelegramError"
    message: str = ""


class InfoRate(BaseModel):
    """
    Класс для вывода информации о количестве успешных и неуспешных отправлений
    """

    messages: list[str] = []
    errors: list[ErrorsSending] = []
    successful_rate: int = 0
    unsuccessful_rate: int = 0
