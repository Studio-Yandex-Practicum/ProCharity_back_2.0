import urllib
from datetime import date
from typing import Dict, Optional

from pydantic import BaseModel, Extra, Field, NonNegativeInt, StrictStr, field_validator, root_validator

from src.core.db.models import ExternalSiteUser
from src.core.enums import TelegramNotificationUsersGroups

from .constants import (
    DATE_FORMAT, TASK_ID_DESCRIPTION, TASK_CATEGORY_ID_DESCRIPTION,
    BONUS_DESCRIPTION, NAME_ORGANIZATION_DESCRIPTION,
    TITLE_DESCRIPTION, DEADLINE_DESCRIPTION, LINK_DESCRIPTION,
    LOCATION_DESCRIPTION, CATEGORY_ID_DESCRIPTION,
    CATEGORY_NAME_DESCRIPTION, PARENT_ID_DESCRIPTION)


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

    id: int = Field(
        ..., ge=1, lt=10**10, description=CATEGORY_ID_DESCRIPTION)
    name: str = Field(
        ..., min_length=2, max_length=100, description=CATEGORY_NAME_DESCRIPTION)
    parent_id: Optional[int] = Field(
        None, ge=1, lt=10**10, description=PARENT_ID_DESCRIPTION)

    @root_validator(skip_on_failure=True)
    def validate_self_parent(cls, values):
        if values["parent_id"] and values["parent_id"] == values["id"]:
            raise ValueError("Категория не может быть дочерней для самой себя.")
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "id": 11,
                "name": "Дизайн сайтов",
                "parent_id": 1,
            }
        }


class CategoryResponse(ResponseBase):
    """Класс модели ответа для Category."""

    id: int
    name: str
    parent_id: Optional[int]
    is_archived: bool


class TaskRequest(RequestBase):
    """Класс модели запроса для Task."""

    id: NonNegativeInt = Field(..., description=TASK_ID_DESCRIPTION)
    title: StrictStr = Field(..., description=TITLE_DESCRIPTION)
    name_organization: StrictStr = Field(..., description=NAME_ORGANIZATION_DESCRIPTION)
    deadline: date = Field(..., format=DATE_FORMAT, description=DEADLINE_DESCRIPTION)
    category_id: NonNegativeInt = Field(..., description=TASK_CATEGORY_ID_DESCRIPTION)
    bonus: NonNegativeInt = Field(..., description=BONUS_DESCRIPTION)
    location: StrictStr = Field(..., description=LOCATION_DESCRIPTION)
    link: StrictStr = Field(..., description=LINK_DESCRIPTION)
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


class Analytic(BaseModel):
    """Класс модели запроса для статистики."""

    command_stats: Dict[str, str] = {}
    reasons_canceling: str = ""
    number_users: int = 0
    all_users_statistic: Dict[str, str] = {}
    active_users_statistic: Dict[str, str] = {}
    tasks: Dict[str, str] = {}
