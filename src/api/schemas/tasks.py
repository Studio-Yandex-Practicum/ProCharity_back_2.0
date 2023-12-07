from datetime import date, datetime

from pydantic import Extra, Field, NonNegativeInt, StrictStr, field_validator

from src.api.constants import DATE_FORMAT, DATE_FORMAT_FOR_TASK_SCHEMA
from src.api.schemas.base import RequestBase, ResponseBase


class TaskRequest(RequestBase):
    """Класс модели запроса для Task."""

    id: NonNegativeInt = Field(..., ge=1, example=1, description="Уникальный идентификатор задачи.")
    title: StrictStr = Field(..., example="Task Title", description="Название задачи.")
    name_organization: StrictStr = Field(
        ..., example="My Organization", description="Название организации, оставившей задачу."
    )
    deadline: date = Field(..., example="31.12.2025", description="Время, до которого нужно выполнить задачу.")
    category_id: NonNegativeInt = Field(
        ..., example=1, description="ID дочерней категории, к которой относится задача."
    )
    bonus: NonNegativeInt = Field(..., ge=1, lt=10, example=5, description="Величина бонуса за выполнение задачи.")
    location: StrictStr = Field(..., example="My Location", description="Локация, в которой находится заказчик задачи.")
    link: StrictStr = Field(..., example="https://example.com", description="Ссылка на сайт, где размещена задача.")
    description: StrictStr = Field(None, example="Task description", description="Описание задачи.")

    @field_validator("deadline", mode="before")
    def str_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, DATE_FORMAT_FOR_TASK_SCHEMA).date()
        return v

    class Config:
        extra = Extra.ignore
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Task Title",
                "name_organization": "My Organization",
                "deadline": "31.12.2025",
                "category_id": 1,
                "bonus": 5,
                "location": "My Location",
                "link": "https://example.com",
                "description": "Task description",
            }
        }


class TaskResponse(ResponseBase):
    """Класс модели ответа для Task."""

    title: StrictStr = Field(..., example="Task Title", description="Название задачи.")
    name_organization: StrictStr = Field(
        ..., example="My Organization", description="Название организации, оставившей задачу."
    )
    deadline: date = Field(
        ..., format=DATE_FORMAT, example="31-12-2025", description="Время, до которого нужно выполнить задачу."
    )
    category_id: NonNegativeInt = Field(
        ..., example=1, description="Показывает, к какой дочерней категории относится задача."
    )
    bonus: NonNegativeInt = Field(..., ge=1, lt=10, example=5, description="Величина бонуса за выполнение задачи.")
    location: StrictStr = Field(..., example="My Location", description="Локация, в которой находится заказчик задачи.")
    link: StrictStr = Field(..., example="https://example.com", description="Ссылка на сайт, где размещена задача.")
    description: StrictStr = Field(None, example="Task description", description="Описание задачи.")
    is_archived: bool = Field(example=False, description="Статус задачи. Если True, то эта задача заархивирована.")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Task Title",
                "name_organization": "My Organization",
                "deadline": "31-12-2025",
                "category_id": 1,
                "bonus": 5,
                "location": "My Location",
                "link": "https://example.com",
                "description": "Task description",
                "is_archived": False,
            }
        }
