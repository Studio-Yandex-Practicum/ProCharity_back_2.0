from pydantic import BaseModel, ConfigDict, Field


class SiteUserCategoriesRequest(BaseModel):
    """Класс модели запроса для user_categories сайта."""

    model_config = ConfigDict(from_attributes=True)
    user_id: int = Field(..., example=1, description="Уникальный идентификатор пользователя.")
    specializations: str = Field(..., example="23, 51", description="Идентификаторы категорий пользователя.")

    class Config:
        json_schema_extra = {"example": {"user_id": 1, "specializations": "23, 51"}}
