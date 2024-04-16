import urllib.parse

from pydantic import BaseModel  # , Field

from src.api.schemas.tasks import TaskRequest


class FeedbackFormQueryParams(BaseModel):
    """Класс формирования параметров запроса для формы обратной связи."""

    external_id: int | None
    telegram_link: str | None
    name: str | None
    surname: str | None
    email: str | None

    def as_url_query(self):
        return f"?{urllib.parse.urlencode(self.model_dump(exclude_none=True))}"


class TaskInfoPageQueryParams(TaskRequest):
    """Класс формирования параметров запроса для страницы с информацией о задании."""

    category: str

    def as_url_query(self):
        return f"?{urllib.parse.urlencode(self.model_dump(exclude_none=True))}"
