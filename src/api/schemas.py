from typing import Optional

from pydantic import BaseModel, Extra, Field, root_validator


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
