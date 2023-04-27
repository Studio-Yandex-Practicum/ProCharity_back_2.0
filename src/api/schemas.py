from datetime import date
from typing import Optional

from pydantic import BaseModel, Extra, Field, root_validator

from .constants import DATE_FORMAT


class ResponseBase(BaseModel):
    """Базовый класс для модели ответа."""

    class Config:
        orm_mode = True


class RequestBase(BaseModel):
    """Базовый класс для модели запроса."""

    class Config:
        extra = Extra.forbid


class CaregoryRequest(RequestBase):
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
    archive: bool


class TaskRequest(RequestBase):
    """Класс модели запроса для Task."""

    id: int = Field(..., ge=1, lt=10**10)
    title: str
    name_organization: str
    deadline: date = Field(..., format=DATE_FORMAT)
    category_id: int = Field(..., ge=1, lt=10**10)
    bonus: int = Field(..., ge=1, lt=11)
    location: str
    link: str
    description: str

    @root_validator(skip_on_failure=True)
    def validate_deadline(cls, values):
        if values["deadline"] < date.today():
            raise ValueError("Дата не может быть меньше текущей.")
        return values


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
    archive: bool
