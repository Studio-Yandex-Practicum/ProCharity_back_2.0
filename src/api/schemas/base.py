from pydantic import BaseModel, ConfigDict


class ResponseBase(BaseModel):
    """Базовый класс для модели ответа."""

    class Config:
        from_attributes = True


class RequestBase(BaseModel):
    """Базовый класс для модели запроса."""

    class Config:
        model_config = ConfigDict(strict=False)
