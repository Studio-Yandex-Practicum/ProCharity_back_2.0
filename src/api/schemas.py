import urllib
from datetime import date
from typing import Optional

from pydantic import BaseModel, Extra, Field, NonNegativeInt, StrictStr, field_validator, root_validator
from typing_extensions import NotRequired, TypedDict

from src.core.db.models import ExternalSiteUser
from src.core.enums import TelegramNotificationUsersGroups

from .constants import DATE_FORMAT


class ResponseBase(BaseModel):
    """Базовый класс для модели ответа."""

    class Config:
        from_attributes = True


class RequestBase(BaseModel):
    """Базовый класс для модели запроса."""

    class Config:
        extra = Extra.forbid


class CategoryRequest(RequestBase):
    """Класс модели запроса для Category."""

    id: int = Field(
        ...,
        ge=1,
        lt=10,
        example=1,
        description="Уникальный идентификатор категории."
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Category Name",
        description="Название категории."
    )
    parent_id: Optional[int] = Field(
        None,
        ge=1,
        lt=10,
        example=1,
        description="Принадлежность к родительской категории. Если null, то это родительская категория."
    )

    @root_validator(skip_on_failure=True)
    def validate_self_parent(cls, values):
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

    id: int = Field(
        ...,
        ge=1,
        lt=10,
        example=1,
        description="Уникальный идентификатор категории."
    )
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        example="Category Name",
        description="Название категории."
    )
    parent_id: Optional[int] = Field(
        None,
        ge=1,
        lt=10,
        example=1,
        description="Принадлежность к родительской категории. Если null, то это родительская категория."
    )
    is_archived: bool = Field(
        example=False,
        description="Статус категории. Если True, то эта категория заархивирована."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Category Name",
                "parent_id": 1,
                "is_archived": False
            }
        }


class TaskRequest(RequestBase):
    """Класс модели запроса для Task."""

    id: NonNegativeInt = Field(
        ...,
        ge=1,
        lt=10,
        example=1,
        description="Уникальный идентификатор задачи."
    )
    title: StrictStr = Field(
        ...,
        example="Task Title",
        description="Название задачи."
    )
    name_organization: StrictStr = Field(
        ...,
        example="My Organization",
        description="Название организации, оставившей задачу."
    )
    deadline: date = Field(
        ...,
        format=DATE_FORMAT,
        example="31-12-2025",
        description="Время, до которого нужно выполнить задачу."
    )
    category_id: NonNegativeInt = Field(
        ...,
        example=1,
        description="Показывает, к какой дочерней категории относится задача."
    )
    bonus: NonNegativeInt = Field(
        ...,
        ge=1,
        lt=10,
        example=5,
        description="Величина бонуса за выполнение задачи."
    )
    location: StrictStr = Field(
        ...,
        example="My Location",
        description="Локация, в которой находится заказчик задачи."
    )
    link: StrictStr = Field(
        ...,
        example="https://example.com",
        description="Ссылка на сайт, где размещена задача."
    )
    description: Optional[StrictStr] = Field(
        None,
        example="Task description",
        description="Описание задачи."
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "Task Title",
                "name_organization": "My Organization",
                "deadline": "31-12-2025",
                "category_id": 1,
                "bonus": 5,
                "location": "My Location",
                "link": "https://example.com",
                "description": "Task description",
            }
        }


class TaskResponse(ResponseBase):
    """Класс модели ответа для Task."""

    title: StrictStr = Field(
        ...,
        example="Task Title",
        description="Название задачи."
    )
    name_organization: StrictStr = Field(
        ...,
        example="My Organization",
        description="Название организации, оставившей задачу."
    )
    deadline: date = Field(
        ...,
        format=DATE_FORMAT,
        example="31-12-2025",
        description="Время, до которого нужно выполнить задачу."
    )
    category_id: NonNegativeInt = Field(
        ...,
        example=1,
        description="Показывает, к какой дочерней категории относится задача."
    )
    bonus: NonNegativeInt = Field(
        ...,
        ge=1,
        lt=10,
        example=5,
        description="Величина бонуса за выполнение задачи."
    )
    location: StrictStr = Field(
        ...,
        example="My Location",
        description="Локация, в которой находится заказчик задачи."
    )
    link: StrictStr = Field(
        ...,
        example="https://example.com",
        description="Ссылка на сайт, где размещена задача."
    )
    description: Optional[StrictStr] = Field(
        None,
        example="Task description",
        description="Описание задачи."
    )
    is_archived: bool = Field(
        example=False,
        description="Статус задачи. Если True, то эта задача заархивирована."
    )

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
                "is_archived": False
            }
        }


class FeedbackFormQueryParams(BaseModel):
    """Класс формирования параметров запроса для формы обратной связи."""

    name: str | None
    surname: str | None
    email: str | None

    def as_url_query(self):
        return f"?{urllib.parse.urlencode(self.dict())}"


class TelegramNotificationRequest(RequestBase):
    """Класс формирования параметров запроса для отправки сообщения определенному пользователю."""

    message: str = Field(..., min_length=2, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Type here your message for user",
            }
        }


class TelegramNotificationUsersRequest(TelegramNotificationRequest):
    """Класс формирования параметров запроса для отправки
    сообщения определенной группе пользователей."""

    mode: TelegramNotificationUsersGroups

    class Config:
        json_schema_extra = {
            "example": {
                "message": "Type here your message for user",
                "mode": "all",
            }
        }


class ExternalSiteUserRequest(RequestBase):
    """Класс модели запроса для ExternalSiteUser."""

    id: int = Field(...)
    id_hash: str = Field(..., max_length=256)
    first_name: Optional[str] = Field(None, max_length=64)
    last_name: Optional[str] = Field(None, max_length=64)
    email: str = Field(..., max_length=48)
    specializations: list[int] | None = None

    def to_orm(self) -> ExternalSiteUser:
        return ExternalSiteUser(
            id=self.id,
            id_hash=self.id_hash,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            specializations=self.specializations,
        )

    @field_validator("specializations", mode="before")
    def specializations_str_validation(cls, value: str):
        if not isinstance(value, str):
            return value
        try:
            new_value = [int(value) for value in value.split(", ")]
            return new_value
        except ValueError:
            raise ValueError('Для передачи строки с числами в поле specializations используйте формат: "1, 2, 3" ')


class Analytic(BaseModel):
    """Класс модели запроса для статистики."""

    command_stats: dict[str, str] = {}
    reasons_canceling: str = ""
    number_users: int = 0
    all_users_statistic: dict[str, str] = {}
    active_users_statistic: dict[str, str] = {}
    tasks: dict[str, str] = {}


class DBStatus(TypedDict):
    """Класс ответа для проверки работы базы данных."""

    status: bool
    last_update: NotRequired[str]
    active_tasks: NotRequired[int]
    db_connection_error: NotRequired[str]


class BotStatus(TypedDict):
    """Класс ответа для проверки работы бота."""

    status: bool
    method: NotRequired[str]
    url: NotRequired[str]
    error: NotRequired[str]


class CommitStatus(TypedDict):
    """Класс ответа для git коммита."""

    last_commit: str
    commit_date: str
    git_tags: list[str]
    commit_error: NotRequired[str]


class HealthCheck(ResponseBase):
    """Класс модели запроса для проверки работы бота."""

    db: DBStatus = {}
    bot: BotStatus = {}
    git: CommitStatus = {}
