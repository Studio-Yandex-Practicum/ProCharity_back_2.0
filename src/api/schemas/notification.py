from typing import AsyncIterable, Iterable, Self

from pydantic import BaseModel, Field

from src.api.schemas.base import RequestBase
from src.core.enums import TelegramNotificationUsersGroups

from .users import UserFilter


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


class TelegramNotificationByFilterRequest(TelegramNotificationRequest):
    """Параметры запроса на отправку сообщения пользователям,
    удовлетворяющим заданным критериям.
    """

    mode: UserFilter = Field(..., description="Критерии отбора пользователей для отправки сообщения")


class Message(TelegramNotificationRequest):
    id_hash: str


class MessageList(RequestBase):
    messages: list[Message]


class ErrorSending(BaseModel):
    """Описание ошибки при отправке сообщения."""

    type: str = "TelegramError"
    message: str = ""


class InfoRate(BaseModel):
    """Информация об успешных и неуспешных отправках сообщений."""

    messages: list[str] = []
    errors: list[ErrorSending] = []
    successful_rate: int = 0
    unsuccessful_rate: int = 0

    def add_result(self, respond: bool, msg: str) -> None:
        """Добавляет результат отправки одного сообщения."""
        if respond:
            self.successful_rate += 1
            self.messages.append(msg)
        else:
            self.unsuccessful_rate += 1
            self.errors.append(ErrorSending(message=msg))

    @staticmethod
    def from_results(results: Iterable[tuple[bool, str]]) -> Self:
        """Создаёт объект класса на основе нескольких результатов отправки."""
        rate = InfoRate()
        for res in results:
            rate.add_result(*res)
        return rate

    @staticmethod
    async def from_results_async(results: AsyncIterable[tuple[bool, str]]) -> Self:
        """Создаёт объект класса на основе нескольких результатов отправки (асинхронно)."""
        rate = InfoRate()
        async for res in results:
            rate.add_result(*res)
        return rate
