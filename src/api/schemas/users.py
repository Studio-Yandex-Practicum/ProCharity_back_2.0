from datetime import datetime

from pydantic import Field

from src.api.schemas.base import ResponseBase


class UserResponse(ResponseBase):
    """Класс схемы ответа для User."""

    telegram_id: int = Field(...)
    first_name: str = Field(...)
    last_name: str = Field(...)
    email: str | None = Field(...)
    username: str = Field(...)
    has_mailing: bool = Field(...)
    banned: bool = Field(...)
    created_at: datetime = Field(..., serialization_alias="date_registration")

    class Config:
        json_schema_extra = {
            "example": {
                "telegram_id": 12345,
                "first_name": "FirstName",
                "last_name": "LastName",
                "email": "example@example.com",
                "username": "UserName",
                "has_mailing": True,
                "banned": False,
                "date_registration": "2000-01-01T00:00:00",
            }
        }
