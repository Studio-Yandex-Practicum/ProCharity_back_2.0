from typing import Literal

from pydantic import BaseModel, Field


class SiteUserCategoriesRequest(BaseModel):
    """Класс модели запроса для user_categories сайта."""

    user_id: int = Field(..., example=1, description="Уникальный идентификатор пользователя.")
    specializations: str = Field(..., example="23, 51", description="Идентификаторы категорий пользователя.")

    class Config:
        json_schema_extra = {"example": {"user_id": 1, "specializations": "23, 51"}}
        from_attributes = True


class SiteBotStatusRequest(BaseModel):
    """Класс модели запроса для bot_status_[fund|folunteer] сайта."""

    user_id: int = Field(..., example=1, description="Уникальный идентификатор пользователя.")
    bot_status: Literal["off", "on"] = Field(..., example="off", description="Статус рассылки бота.")

    class Config:
        json_schema_extra = {"example": {"user_id": 1, "bot_status": "on"}}
        from_attributes = True
