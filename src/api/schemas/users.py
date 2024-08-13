from datetime import datetime
from typing import Annotated

from fastapi import Query
from pydantic import BaseModel, Field

from src.api.schemas.base import PaginateBase, ResponseBase
from src.core.enums import UserRoleFilterValues, UserStatusFilterValues


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


class UsersPaginatedResponse(PaginateBase):
    """Класс схемы постраничного ответа для User."""

    result: list[UserResponse] | None


class UserFilter(BaseModel):
    """Поля для фильтрации пользователей."""

    role: Annotated[
        UserRoleFilterValues | None,
        Query(None, title="роль пользователя", description="Фильтрация на основе поля role в users"),
    ] = None
    status: Annotated[
        UserStatusFilterValues | None,
        Query(
            None,
            title="Статус модерации пользователя",
            description=(
                "Фильтрация на основе поля moderation_status в связанном с данным пользователем user "
                "пользователе сайта external_site_user"
            ),
        ),
    ] = None
    authorization: Annotated[
        bool | None,
        Query(
            None,
            title="Признак авторизации пользователя",
            description="Фильтрация на основе связи пользователей user с пользователем сайта external_site_user",
        ),
    ] = None
