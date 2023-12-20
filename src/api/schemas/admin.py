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
    token: str = Field(..., description="Invitation token")
    first_name: Optional[str] = Field(None, max_length=64, description="User' First Name.")
    last_name: Optional[str] = Field(None, max_length=64, description="User' Last Name.")
    password: str = Field(..., description="Account password.")


class UserRead(schemas.BaseUser[int]):
    pass
