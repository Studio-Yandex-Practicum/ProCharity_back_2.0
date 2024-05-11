from datetime import datetime

from pydantic import Field

from src.api.schemas.base import ResponseBase


class UserResponse(ResponseBase):
    """Класс схемы ответа для User."""

    telegram_id: int
    first_name: str
    last_name: str
    email: str | None
    username: str
    has_mailing: bool
    banned: bool
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


class UsersPaginatedResponse(ResponseBase):
    """Класс схемы постраничного ответа для User."""

    total: int | None
    pages: int | None
    current_page: int | None
    next_page: int | None
    previous_page: int | None
    next_url: str | None
    previous_url: str | None
    result: list[UserResponse] | None
