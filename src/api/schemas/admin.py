import re
from typing import Never

from fastapi.param_functions import Form
from fastapi_users import schemas
from pydantic import BaseModel, EmailStr, Field, ValidationInfo, field_validator

from src.api.constants import PASSWORD_POLICY
from src.core.exceptions import InvalidPassword, NullException


class AdminUserCreate(schemas.CreateUpdateDictModel):
    token: str = Field(..., description="Invitation token.")
    first_name: str | None = Field(None, max_length=64, description="User's First Name.")
    last_name: str | None = Field(None, max_length=64, description="User's Last Name.")
    password: str = Field(..., description="Account password.")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if re.match(PASSWORD_POLICY, value) is None:
            raise InvalidPassword
        return value


class AdminUserRead(schemas.BaseUser[int]):
    pass


class AdminUserUpdate(schemas.BaseUserUpdate):
    first_name: str | None = Field(None, max_length=64, description="User's First Name.")
    last_name: str | None = Field(None, max_length=64, description="User's Last Name.")

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str | Never:
        if re.match(PASSWORD_POLICY, value) is None:
            raise InvalidPassword
        return value

    @field_validator("*", mode="before")
    @classmethod
    def validate_all(cls, value, info: ValidationInfo):
        if value is None:
            raise NullException(info.field_name)
        return value


class CustomBearerResponse(BaseModel):
    access_token: str
    refresh_token: str


class OAuth2PasswordRequestForm:
    def __init__(
        self,
        *,
        grant_type: str | None = Form(default=None, regex="password"),
        email: EmailStr = Form(),
        password: str = Form(),
        scope: str = Form(default=""),
        client_id: str | None = Form(default=None),
        client_secret: str | None = Form(default=None),
    ):
        self.grant_type = grant_type
        self.username = email
        self.password = password
        self.scopes = scope.split()
        self.client_id = client_id
        self.client_secret = client_secret


class InvitationCreateSchema(BaseModel):
    email: EmailStr
    is_superuser: bool | None = Field(False)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "is_superuser": "False",
            }
        }
