from pydantic import BaseModel, ConfigDict


class ResponseBase(BaseModel):
    """Базовый класс для модели ответа."""

    model_config = ConfigDict(from_attributes=True)


class RequestBase(BaseModel):
    """Базовый класс для модели запроса."""

    model_config = ConfigDict(strict=False)


class PaginateBase(ResponseBase):
    """Базовый класс для схем с постраничным ответом."""

    total: int | None
    pages: int | None
    current_page: int | None
    next_page: int | None
    previous_page: int | None
    next_url: str | None
    previous_url: str | None
