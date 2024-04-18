from pydantic import Field

from src.api.schemas.base import ResponseBase


class SiteUserCategoriesRequest(ResponseBase):
    """Класс модели запроса для user_categories сайта."""

    user_id: int = Field(..., example=1, description="Уникальный идентификатор пользователя.")
    specializations: str = Field(..., example="23, 51", description="Идентификаторы категорий пользователя.")

    class Config:
        json_schema_extra = {"example": {"user_id": 1, "specializations": "23, 51"}}
