import urllib.parse
from datetime import date

from pydantic import BaseModel, NonNegativeInt, StrictFloat


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

    id: NonNegativeInt
    title: str
    name_organization: str | None
    legal_address: str | None
    fund_city: str | None
    fund_rating: StrictFloat | None
    fund_site: str | None
    yb_link: str | None
    vk_link: str | None
    fund_sections: str | None
    deadline: date | None
    category: str | None
    bonus: NonNegativeInt | None
    location: str | None
    link: str | None
    description: str | None
