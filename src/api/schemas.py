from datetime import date
from typing import Optional
import urllib

from pydantic import BaseModel, Extra, Field, HttpUrl, NonNegativeInt, StrictStr, root_validator

from .constants import DATE_FORMAT


class ResponseBase(BaseModel):
    """Базовый класс для модели ответа."""

    class Config:
        orm_mode = True


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
    link: HttpUrl = Field(...)
    description: Optional[StrictStr] = None

    class Config:
        schema_extra = {
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


class QueryParams(BaseModel):
    name: Optional[str] = "Имя"
    surname: Optional[str] = "Фамилия"

    @classmethod
    def as_dict(cls, name, surname):
        return {"name": name, "surname": surname}

    @classmethod
    def as_url_query(cls, name, surname):
        return f"?{urllib.parse.urlencode(cls.as_dict(name, surname))}"

