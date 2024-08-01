from pydantic import Field, model_validator

from src.api.schemas.base import RequestBase, ResponseBase


class CategoryRequest(RequestBase):
    """Класс модели запроса для Category."""

    id: int = Field(..., example=1, description="Уникальный идентификатор категории.")
    name: str = Field(..., min_length=2, max_length=100, example="Category Name", description="Название категории.")
    parent_id: int | None = Field(
        None,
        example=1,
        description="Принадлежность к родительской категории. Если null, то это родительская категория.",
    )

    @model_validator(mode="before")
    @classmethod
    def validate_self_parent(cls, values: dict) -> dict:
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
    parent_id: int | None = Field(
        None,
        example=1,
        description="Принадлежность к родительской категории. Если null, то это родительская категория.",
    )
    is_archived: bool = Field(
        example=False, description="Статус категории. Если True, то эта категория заархивирована."
    )

    class Config:
        json_schema_extra = {"example": {"id": 1, "name": "Category Name", "parent_id": 1, "is_archived": False}}
