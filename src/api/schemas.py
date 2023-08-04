import urllib
from datetime import date
from typing import Optional

from pydantic import BaseModel, Extra, Field, NonNegativeInt, StrictStr, field_validator, root_validator

from src.core.db.models import ExternalSiteUser
from src.core.enums import TelegramNotificationUsersGroups

from .constants import DATE_FORMAT


class ResponseBase(BaseModel):
    """Базовый класс для модели ответа."""

    class Config:
        from_attributes = True


class RequestBase(BaseModel):
    """Базовый класс для модели запроса."""

    class Config:
        extra = Extra.forbid


class CategoryRequest(RequestBase):
    """Класс модели запроса для Category."""

    id: int = Field(..., ge=1, lt=10**10)
    name: str = Field(..., min_length=2, max_length=100)
    parent_id: Optional[int] = Field(None, ge=1, lt=10**10)

    @root_validator(skip_on_failure=True)
    def validate_self_parent(cls, values):
        if values["parent_id"] and values["parent_id"] == values["id"]:
            raise ValueError("Категория не может быть дочерней для самой себя.")
        return values


class CategoryResponse(ResponseBase):
    """Класс модели ответа для Category."""

    id: int
    name: str
    parent_id: Optional[int]
    is_archived: bool


class TaskRequest(RequestBase):
    """Класс модели запроса для Task."""

    id: NonNegativeInt = Field(...)
    title: StrictStr = Field(...)
    name_organization: StrictStr = Field(...)
    deadline: date = Field(..., format=DATE_FORMAT)
    category_id: NonNegativeInt = Field(...)
    bonus: NonNegativeInt = Field(...)
    location: StrictStr = Field(...)
    link: StrictStr = Field(...)
    description: Optional[StrictStr] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Task Title",
                "name_organization": "My Organization",
                "deadline": "2025-12-31",
                "category_id": 1,
                "bonus": 5,
                "location": "My Location",
                "link": "https://example.com",
                "description": "Task description",
            }
        }


class TaskResponse(ResponseBase):
    """Класс модели ответа для Task."""

    title: str
    name_organization: str
    deadline: date
    category_id: int
    bonus: int
    location: str
    link: str
    description: str
    is_archived: bool


class FeedbackFormQueryParams(BaseModel):
    """Класс формирования параметров запроса для формы обратной связи."""

    name: str | None
    surname: str | None
    email: str | None

    def as_url_query(self):
        return f"?{urllib.parse.urlencode(self.dict())}"


class TelegramNotificationRequest(RequestBase):
    """Класс формирования параметров запроса для отправки сообщения определенному пользователю."""

    message: str = Field(..., min_length=2, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Type here your message for user",
            }
        }


class TelegramNotificationUsersRequest(TelegramNotificationRequest):
    """Класс формирования параметров запроса для отправки
    сообщения определенной группе пользователей."""

    mode: TelegramNotificationUsersGroups

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Type here your message for user",
                "mode": "all",
            }
        }


class ExternalSiteUserRequest(RequestBase):
    """Класс модели запроса для ExternalSiteUser."""

    id: int = Field(...)
    id_hash: str = Field(..., max_length=256)
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    email: str = Field(..., max_length=48)
    specializations: list[int] | None = None

    def to_orm(self) -> ExternalSiteUser:
        return ExternalSiteUser(
            id=self.id,
            id_hash=self.id_hash,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            specializations=self.specializations,
        )

    @field_validator("specializations", mode="before")
    def specializations_str_validation(cls, value: str):
        if not isinstance(value, str):
            return value
        try:
            new_value = [int(value) for value in value.split(", ")]
            return new_value
        except ValueError:
            raise ValueError('Для передачи строки с числами в поле specializations используйте формат: "1, 2, 3" ')
