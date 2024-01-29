from datetime import date, datetime

from pydantic import Extra, Field, NonNegativeInt, StrictFloat, StrictStr, field_validator

from src.api.constants import DATE_FORMAT, DATE_FORMAT_FOR_TASK_SCHEMA
from src.api.schemas.base import RequestBase, ResponseBase


class TaskRequest(RequestBase):
    """Класс модели запроса для Task."""

    id: NonNegativeInt = Field(..., ge=1, example=1, description="Уникальный идентификатор задачи.")
    title: StrictStr = Field(..., example="Task Title", description="Название задачи.")
    name_organization: StrictStr = Field(..., example="My Fund", description="Название Фонда.")
    legal_address: StrictStr = Field(..., example="Fund Legal Adress", description="Юридический адрес Фонда.")
    fund_city: StrictStr = Field(..., example="Fund City", description="Фактический адрес Фонда.")
    fund_rating: StrictFloat = Field(..., example=78.65, description="Рейтинг Фонда.")
    fund_site: StrictStr = Field(..., example="https://fundexample.com", description="Страница Фонда в сети интернет.")
    yb_link: StrictStr = Field(..., example="https://youtubeexample.com", description="Страница Фонда в youtube.")
    vk_link: StrictStr = Field(..., example="https://vkexample.com", description="Страница Фонда в VK.")
    fund_sections: list[NonNegativeInt] = Field(..., example=[1, 7], description="Сферы деятельности Фонда.")
    deadline: date = Field(..., format=DATE_FORMAT, example="31-12-2025", description="Дедлайн выполнения задачи.")
    category_id: NonNegativeInt = Field(
        ..., example=1, description="ID дочерней категории, к которой относится задача."
    )
    bonus: NonNegativeInt = Field(..., ge=1, lt=10, example=5, description="Количество бонусов за выполнение задачи.")
    location: StrictStr = Field(..., example="Task Location", description="Место выполнения задачи.")
    link: StrictStr = Field(..., example="https://example.com", description="Ссылка на страницу задачи.")
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
                "name_organization": "My Fund",
                "legal_address": "Fund Legal Adress",
                "fund_city": "Fund City",
                "fund_rating": 78.65,
                "fund_site": "https://fundexample.com",
                "yb_link": "https://youtubeexample.com",
                "vk_link": "https://vkexample.com",
                "fund_sections": [1, 7],
                "deadline": "31.12.2025",
                "category_id": 1,
                "bonus": 5,
                "location": "Task Location",
                "link": "https://example.com",
                "description": "Task description",
            }
        }


class TaskResponse(ResponseBase):
    """Класс модели ответа для Task."""

    title: StrictStr = Field(..., example="Task Title", description="Название задачи.")
    name_organization: StrictStr = Field(..., example="My Fund", description="Название Фонда.")
    legal_address: StrictStr = Field(..., example="Fund Legal Adress", description="Юридический адрес Фонда.")
    fund_city: StrictStr = Field(..., example="Fund City", description="Фактический адрес Фонда.")
    fund_rating: StrictFloat = Field(..., example=78.65, description="Рейтинг Фонда.")
    fund_site: StrictStr = Field(..., example="https://fundexample.com", description="Страница Фонда в сети интернет.")
    yb_link: StrictStr = Field(..., example="https://youtubeexample.com", description="Страница Фонда в youtube.")
    vk_link: StrictStr = Field(..., example="https://vkexample.com", description="Страница Фонда в VK.")
    fund_sections: list[NonNegativeInt] = Field(..., example=[1, 7], description="Сферы деятельности Фонда.")
    deadline: date = Field(..., format=DATE_FORMAT, example="31-12-2025", description="Дедлайн выполнения задачи.")
    category_id: NonNegativeInt = Field(
        ..., example=1, description="ID дочерней категории, к которой относится задача."
    )
    bonus: NonNegativeInt = Field(..., ge=1, lt=10, example=5, description="Количество бонусов за выполнение задачи.")
    location: StrictStr = Field(..., example="Task Location", description="Место выполнения задачи.")
    link: StrictStr = Field(..., example="https://example.com", description="Ссылка на страницу задачи.")
    description: StrictStr = Field(None, example="Task description", description="Описание задачи.")
    is_archived: bool = Field(example=False, description="Статус задачи. Если True, то эта задача заархивирована.")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Task Title",
                "name_organization": "My Fund",
                "legal_address": "Fund Legal Adress",
                "fund_city": "Fund City",
                "fund_rating": 78.65,
                "fund_site": "https://fundexample.com",
                "yb_link": "https://youtubeexample.com",
                "vk_link": "https://vkexample.com",
                "fund_sections": [1, 7],
                "deadline": "31-12-2025",
                "category_id": 1,
                "bonus": 5,
                "location": "Task Location",
                "link": "https://example.com",
                "description": "Task description",
                "is_archived": False,
            }
        }
