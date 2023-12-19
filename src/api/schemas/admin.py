from typing import Optional

from fastapi_users import schemas
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


class UserCreate(schemas.CreateUpdateDictModel):
    # хочется исправить на "Invitation token."
    token: str = Field(..., description="Invitation token")
    # хочется исправить на "User's First Name."
    first_name: Optional[str] = Field(None, max_length=64, description="User' First Name.")
    # хочется исправить на "User's Last Name."
    last_name: Optional[str] = Field(None, max_length=64, description="User' Last Name.")
    password: str = Field(..., description="Account password.")


class UserRead(schemas.BaseUser[int]):
    pass
