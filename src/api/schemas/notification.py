import urllib

from pydantic import BaseModel, Field

from src.api.schemas.base import RequestBase
from src.core.enums import TelegramNotificationUsersGroups


class FeedbackFormQueryParams(BaseModel):
    """Класс формирования параметров запроса для формы обратной связи."""

    name: str | None
    surname: str | None
    email: str | None

    def as_url_query(self):
        return f"?{urllib.parse.urlencode(self.dict())}"


class TelegramNotificationRequest(RequestBase):
    """
    Класс формирования параметров запроса для отправки
    сообщения определенному пользователю.
    """

    message: str = Field(..., min_length=1)


class TelegramNotificationUsersRequest(TelegramNotificationRequest):
    """Класс формирования параметров запроса для отправки
    сообщения определенной группе пользователей."""

    mode: TelegramNotificationUsersGroups


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
