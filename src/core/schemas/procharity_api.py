from pydantic import BaseModel, Field


class SiteUserCategoriesRequest(BaseModel):
    """Класс модели запроса для user_categories сайта."""

    user_id: int = Field(..., example=1, description="Уникальный идентификатор пользователя.")
    specializations: str = Field(..., example="23, 51", description="Идентификаторы категорий пользователя.")

    class Config:
        json_schema_extra = {"example": {"user_id": 1, "specializations": "23, 51"}}
        from_attributes = True
