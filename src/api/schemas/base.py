from pydantic import BaseModel, ConfigDict


class ResponseBase(BaseModel):
    """Базовый класс для модели ответа."""

    model_config = ConfigDict(from_attributes=True)


class RequestBase(BaseModel):
    """Базовый класс для модели запроса."""

    model_config = ConfigDict(strict=False)
