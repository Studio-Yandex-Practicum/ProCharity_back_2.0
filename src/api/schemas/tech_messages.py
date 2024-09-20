from datetime import datetime

from src.api.schemas.base import PaginateBase, RequestBase, ResponseBase


class TechMessageResponce(ResponseBase):
    """Класс схемы ответа."""

    id: int
    text: str
    was_read: bool
    created_at: datetime


class TechMessageRequest(RequestBase):
    """Класс схемы запроса."""

    was_read: bool


class TechMessagePaginateResponse(PaginateBase):
    """Класс схемы постраничного ответа."""

    result: list[TechMessageResponce] | None
