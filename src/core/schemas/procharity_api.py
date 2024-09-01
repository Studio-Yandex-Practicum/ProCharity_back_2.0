from typing import Literal

from pydantic import BaseModel, Field

from src.bot.constants.enum import CANCEL_RESPOND_REASONS
from src.core.enums import UserResponseAction


class SiteUserCategoriesRequest(BaseModel):
    """Класс модели запроса для user_categories сайта."""

    user_id: int = Field(..., example=1, description="Уникальный идентификатор пользователя.")
    specializations: str = Field(..., example="23, 51", description="Идентификаторы категорий пользователя.")

    class Config:
        json_schema_extra = {"example": {"user_id": 1, "specializations": "23, 51"}}
        from_attributes = True


class SiteBotStatusFundRequest(BaseModel):
    """Класс модели запроса для bot_status_fund сайта."""

    user_id: int = Field(..., example=1, description="Уникальный идентификатор пользователя.")
    bot_status: Literal["off", "on"] = Field(..., example="off", description="Статус рассылки бота.")
    bot_blocked: bool = Field(..., description="Признак блокировки бота пользователем.")
    has_mailing_profile: bool | None = Field(None, description="Признак рассылки .")
    has_mailing_my_tasks: bool | None = Field(None, description="Признак рассылки .")
    has_mailing_procharity: bool | None = Field(None, description="Признак рассылки .")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "bot_status": "on",
                "bot_blocked": "false",
                "has_mailing_profile": "true",
                "has_mailing_my_tasks": "true",
                "has_mailing_procharity": "true",
            }
        }
        from_attributes = True


class SiteBotStatusVolunteerRequest(SiteBotStatusFundRequest):
    """Класс модели запроса для bot_status_folunteer сайта."""

    has_mailing_new_tasks: bool = Field(..., description="Включена ли рассылка на новые задания.")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "bot_status": "on",
                "bot_blocked": "false",
                "has_mailing_new_tasks": "true",
                "has_mailing_profile": "true",
                "has_mailing_my_tasks": "true",
                "has_mailing_procharity": "true",
            }
        }
        from_attributes = True


class SiteBotRespondRequest(BaseModel):
    """Класс модели запроса для bot_respond сайта."""

    user_id: int = Field(..., example=123, description="Уникальный идентификатор пользователя.")
    task_id: int = Field(..., example=1424222, description="Уникальный идентификатор задачи.")
    status: UserResponseAction = Field(
        ...,
        example="respond",
        description="Статус отклика на задачу ('respond' - отклик, 'cancel_respond' - отмена отклика).",
    )
    cancel_reason: CANCEL_RESPOND_REASONS | None = Field(None, example="Другое", description="Причина отмены отклика")

    class Config:
        json_schema_extra = {"example": {"user_id": 123, "task_id": 1424222, "status": "respond"}}
        from_attributes = True
