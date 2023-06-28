from enum import StrEnum
from pydantic import Field
from src.api.schemas import RequestBase
from src.core.enums import TelegramNotificationUsersGroups


class TelegramNotificationRequest(RequestBase):
    """Класс формирования параметров запроса для отправки
     сообщения определенной группе пользователей."""
    message: str = Field(..., min_length=2, max_length=500)
    mode: TelegramNotificationUsersGroups

    class Config:
        schema_extra = {
            "example": {
                "message": "Type here your message for user",
                "mode": "all",
            }
        }
