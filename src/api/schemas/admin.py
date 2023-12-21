import re

from fastapi_users import schemas
from pydantic import Field, validator

from src.api.constants import PASSWORD_POLICY
from src.api.schemas.base import RequestBase
from src.core.exceptions.exceptions import InvalidPassword


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
    token: str = Field(..., description="Invitation token.")
    first_name: str | None = Field(None, max_length=64, description="User's First Name.")
    last_name: str | None = Field(None, max_length=64, description="User's Last Name.")
    password: str = Field(..., description="Account password.")

    @validator("password")
    def validate_password(cls, value: str):
        if re.match(PASSWORD_POLICY, value) is None:
            raise InvalidPassword
        return value


class UserRead(schemas.BaseUser[int]):
    pass
