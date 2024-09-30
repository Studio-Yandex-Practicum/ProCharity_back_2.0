import urllib.parse

from pydantic import BaseModel, NonNegativeInt


class QueryParams(BaseModel):
    """Параметры запроса."""

    def as_url_query(self):
        return f"?{urllib.parse.urlencode(self.model_dump(exclude_none=True))}"


class FeedbackFormQueryParams(QueryParams):
    """Параметры запроса для формы обратной связи."""

    external_id: int | None
    telegram_link: str | None
    name: str | None
    surname: str | None
    email: str | None


class TaskInfoPageQueryParams(QueryParams):
    """Параметры запроса для страницы с информацией о задании."""

    task_id: NonNegativeInt
