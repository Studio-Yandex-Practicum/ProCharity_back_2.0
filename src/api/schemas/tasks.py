from datetime import date, datetime

from pydantic import Field, NonNegativeInt, RootModel, StrictFloat, field_validator

from src.api.constants import DATE_FORMAT, DATE_FORMAT_FOR_TASK_SCHEMA
from src.api.schemas.base import RequestBase, ResponseBase


class TaskRequest(RequestBase):
    """Класс модели запроса для Task."""

    id: NonNegativeInt = Field(..., ge=1, examples=[1], description="Уникальный идентификатор задачи.")
    title: str = Field(..., examples=["Task Title"], description="Название задачи.")
    name_organization: str | None = Field(None, examples=["My Fund"], description="Название Фонда.")
    legal_address: str | None = Field(None, examples=["Fund Legal Adress"], description="Юридический адрес Фонда.")
    fund_city: str | None = Field(None, examples=["Fund City"], description="Фактический адрес Фонда.")
    fund_rating: StrictFloat | None = Field(None, examples=[78.65], description="Рейтинг Фонда.")
    fund_site: str | None = Field(
        None, examples=["https://fundexample.com"], description="Страница Фонда в сети интернет."
    )
    yb_link: str | None = Field(None, examples=["https://youtubeexample.com"], description="Страница Фонда в youtube.")
    vk_link: str | None = Field(None, examples=["https://vkexample.com"], description="Страница Фонда в VK.")
    fund_sections: str | None = Field(None, examples=[1, 7], description="Сферы деятельности Фонда.")
    deadline: date | None = Field(
        None, format=DATE_FORMAT, examples=["23.11.2024"], description="Дедлайн выполнения задачи."
    )
    category_id: NonNegativeInt | None = Field(
        None, examples=[1], description="ID дочерней категории, к которой относится задача."
    )
    bonus: NonNegativeInt | None = Field(
        None, ge=1, lt=11, examples=[5], description="Количество бонусов за выполнение задачи."
    )
    location: str | None = Field(None, examples=["Task Location"], description="Место выполнения задачи.")
    link: str | None = Field(None, examples=["https://examples.com"], description="Ссылка на страницу задачи.")
    description: str | None = Field(None, examples=["Task description"], description="Описание задачи.")

    @field_validator("deadline", mode="before")
    @classmethod
    def str_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, DATE_FORMAT_FOR_TASK_SCHEMA).date()
        return v


class TasksRequest(RootModel[list[TaskRequest]]):
    """Список задач."""

    root: list[TaskRequest]


class TaskResponse(ResponseBase):
    """Класс модели ответа для Task."""

    title: str = Field(..., examples=["Task Title"], description="Название задачи.")
    name_organization: str | None = Field(None, examples=["My Fund"], description="Название Фонда.")
    legal_address: str | None = Field(None, examples=["Fund Legal Address"], description="Юридический адрес Фонда.")
    fund_city: str | None = Field(None, examples=["Fund City"], description="Фактический адрес Фонда.")
    fund_rating: StrictFloat | None = Field(None, examples=[78.65], description="Рейтинг Фонда.")
    fund_site: str | None = Field(
        None, examples=["https://fundexample.com"], description="Страница Фонда в сети интернет."
    )
    yb_link: str | None = Field(None, examples=["https://youtubeexample.com"], description="Страница Фонда в youtube.")
    vk_link: str | None = Field(None, examples=["https://vkexample.com"], description="Страница Фонда в VK.")
    fund_sections: list[NonNegativeInt] | None = Field(None, examples=[1, 7], description="Сферы деятельности Фонда.")
    deadline: date = Field(..., format=DATE_FORMAT, examples=["23.11.2024"], description="Дедлайн выполнения задачи.")
    category_id: NonNegativeInt = Field(
        ..., examples=[1], description="ID дочерней категории, к которой относится задача."
    )
    bonus: NonNegativeInt = Field(
        ..., ge=1, lt=10, examples=[5], description="Количество бонусов за выполнение задачи."
    )
    location: str = Field(..., examples=["Task Location"], description="Место выполнения задачи.")
    link: str = Field(..., examples=["https://examples.[com"], description="Ссылка на страницу задачи.")
    description: str | None = Field(None, examples=["Task description"], description="Описание задачи.")
    is_archived: bool = Field(examples=[False], description="Статус задачи. Если True, то эта задача заархивирована.")
