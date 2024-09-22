from pydantic import EmailStr, Field, field_validator

from src.api.schemas.base import RequestBase
from src.core.enums import UserRoles, UserStatus


class BaseExternalSiteUser(RequestBase):
    """Базовый класс схемы для ExternalSiteUser."""

    first_name: str | None = Field(None, max_length=64)
    last_name: str | None = Field(None, max_length=64)
    email: EmailStr | None = Field(None, max_length=48)
    moderation_status: str | None = Field(None)
    has_mailing_profile: bool = None
    has_mailing_my_tasks: bool = None
    has_mailing_procharity: bool = None

    @field_validator("moderation_status")
    @classmethod
    def moderation_status_validation(cls, value: str) -> str | None:
        try:
            value = UserStatus.__members__[value]
            return value
        except KeyError as exc:
            raise ValueError(
                "Для передачи статуса пользователя используйте предусмотренные варианты: WAIT, MODERATED и т.д."
            ) from exc


class BaseExternalSiteUserVolunteer(RequestBase):
    """Базовый класс схемы для ExternalSiteUser (Volunteer)."""

    specializations: list[int] | None = Field(None)
    has_mailing_new_tasks: bool = None

    @classmethod
    def validate_unique_values(cls, values: list[int]) -> list[int]:
        if len(set(values)) != len(values):
            raise ValueError("В поле specializations не должно быть дублирующихся значений")
        return values

    @field_validator("specializations", mode="before")
    @classmethod
    def specializations_validation(cls, value: str | list[int]) -> list[int] | None:
        if not isinstance(value, str):
            return cls.validate_unique_values(value)
        if value == "":
            return []
        try:
            new_value = [int(value) for value in value.replace(" ", "").split(",")]
        except ValueError as exc:
            raise ValueError(
                'Для передачи строки с числами в поле specializations используйте формат: "1, 2, 3"'
            ) from exc
        return cls.validate_unique_values(new_value)


class ExternalSiteUserRequest(BaseExternalSiteUser):
    """Класс схемы запроса для ExternalSiteUser."""

    external_id: int = Field(..., gt=0, alias="user_id")
    id_hash: str = Field(..., min_length=1, max_length=256)
    first_name: str = Field(..., max_length=64)
    last_name: str = Field(..., max_length=64)
    email: EmailStr = Field(..., max_length=48)
    moderation_status: str = Field(...)


class ExternalSiteVolunteerRequest(ExternalSiteUserRequest, BaseExternalSiteUserVolunteer):
    """Класс схемы запроса для ExternalSiteUser (Volunteer)."""

    specializations: list[int]

    def get_role(self) -> UserRoles:
        return UserRoles.VOLUNTEER


class ExternalSiteFundRequest(ExternalSiteUserRequest):
    """Класс схемы запроса для ExternalSiteUser (Fund)."""

    def get_role(self) -> UserRoles:
        return UserRoles.FUND


class ExternalSiteVolunteerPartialUpdate(BaseExternalSiteUser, BaseExternalSiteUserVolunteer):
    """Класс схемы обновления для ExternalSiteUser (Volunteer)."""

    pass


class ExternalSiteFundPartialUpdate(BaseExternalSiteUser):
    """Класс схемы обновления для ExternalSiteUser (Fund)."""

    pass
