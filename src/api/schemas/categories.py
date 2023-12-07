from typing import Optional

from pydantic import Field, root_validator

from src.api.schemas.base import RequestBase, ResponseBase


class CategoryRequest(RequestBase):
    """Класс модели запроса для Category."""

    id: int = Field(..., example=1, description="Уникальный идентификатор категории.")
    name: str = Field(..., min_length=2, max_length=100, example="Category Name", description="Название категории.")
    parent_id: Optional[int] = Field(
        None,
        example=1,
        description="Принадлежность к родительской категории. Если null, то это родительская категория.",
    )

    @root_validator(skip_on_failure=True)
    def validate_self_parent(cls, values):
        if values["parent_id"] and values["parent_id"] == values["id"]:
            raise ValueError("Категория не может быть дочерней для самой себя.")
        return values

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Category Name",
                "parent_id": 1,
            }
        }


class CategoryResponse(ResponseBase):
    """Класс модели ответа для Category."""

    id: int = Field(..., example=1, description="Уникальный идентификатор категории.")
    name: str = Field(..., min_length=2, max_length=100, example="Category Name", description="Название категории.")
    parent_id: Optional[int] = Field(
        None,
        example=1,
        description="Принадлежность к родительской категории. Если null, то это родительская категория.",
    )
    is_archived: bool = Field(
        example=False, description="Статус категории. Если True, то эта категория заархивирована."
    )

    class Config:
        json_schema_extra = {"example": {"id": 1, "name": "Category Name", "parent_id": 1, "is_archived": False}}
