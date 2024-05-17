from typing_extensions import NotRequired, TypedDict

from src.api.schemas.base import ResponseBase


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

    db: DBStatus
    bot: BotStatus
    git: CommitStatus
