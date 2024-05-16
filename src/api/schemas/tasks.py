from datetime import date, datetime

from pydantic import Field, PositiveInt, RootModel, StrictFloat, field_validator

from src.api.constants import DATE_FORMAT, DATE_FORMAT_FOR_TASK_SCHEMA
from src.api.schemas.base import RequestBase, ResponseBase


class TaskCommonFieldsMixin:
    """Набор общих полей для схем модели Task."""

    title: str = Field(..., examples=["Example Task"], description="Название задачи.")
    name_organization: str = Field(..., examples=["Example Fund"], description="Название Фонда.")
    legal_address: str | None = Field(None, examples=["Fund Legal Address"], description="Юридический адрес Фонда.")
    fund_city: str | None = Field(None, examples=["Fund City"], description="Фактический адрес Фонда.")
    fund_rating: StrictFloat | None = Field(None, examples=[78.65], description="Рейтинг Фонда.")
    fund_site: str | None = Field(
        None, examples=["https://example-fund.com"], description="Страница Фонда в сети Интернет."
    )
    fund_link: str | None = Field(
        None, examples=["https://mainsite.com/funds/1234"], description="Публичная страница Фонда на основном сайте."
    )
    yb_link: str | None = Field(
        None, examples=["https://youtube.com/@example_fund"], description="Страница Фонда в Youtube."
    )
    vk_link: str | None = Field(None, examples=["https://vk.com/example_fund"], description="Страница Фонда в VK.")
    fund_sections: str | None = Field(None, examples=["1, 7"], description="Сферы деятельности Фонда.")
    deadline: date = Field(..., format=DATE_FORMAT, examples=["23.11.2024"], description="Дедлайн выполнения задачи.")
    category_id: PositiveInt = Field(
        ..., examples=[1], description="ID дочерней категории, к которой относится задача."
    )
    bonus: PositiveInt = Field(..., ge=1, le=10, examples=[5], description="Количество бонусов за выполнение задачи.")
    location: str = Field(..., examples=["Task Location"], description="Место выполнения задачи.")
    link: str = Field(..., examples=["https://mainsite.com/tasks/1234"], description="Ссылка на страницу задачи.")
    description: str = Field(..., examples=["Task description"], description="Описание задачи.")


class TaskRequest(RequestBase, TaskCommonFieldsMixin):
    """Схема запроса для модели Task."""

    id: PositiveInt = Field(..., examples=[1], description="Уникальный идентификатор задачи.")

    @field_validator("deadline", mode="before")
    @classmethod
    def str_to_date(cls, v: object) -> object:
        if isinstance(v, str):
            return datetime.strptime(v, DATE_FORMAT_FOR_TASK_SCHEMA).date()
        return v


class TasksRequest(RootModel[list[TaskRequest]]):
    """Схема запроса для списка задач."""

    root: list[TaskRequest]


class TaskResponse(ResponseBase, TaskCommonFieldsMixin):
    """Схема ответа для модели Task."""

    is_archived: bool = Field(..., examples=[False], description="Является ли задача архивной.")
