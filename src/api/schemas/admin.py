from pydantic import Field

from src.api.schemas.base import RequestBase


class AdminUserRequest(RequestBase):
    """Класс модели запроса для AdminUser."""

    email: str = Field(..., max_length=48)
    password: str = Field(..., max_length=48)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "email",
                "password": "password",
            }
        }
