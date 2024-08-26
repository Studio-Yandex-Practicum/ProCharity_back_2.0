from pydantic import EmailStr, Field, field_validator

from src.api.schemas.base import RequestBase
from src.core.db.models import ExternalSiteUser
from src.core.enums import UserRoles, UserStatus


class BaseExternalSiteUser(RequestBase):
    """Базовый класс схемы для ExternalSiteUser."""

    first_name: str | None = Field(None, max_length=64)
    last_name: str | None = Field(None, max_length=64)
    email: EmailStr | None = Field(None, max_length=48)
    moderation_status: str | None = Field(None)

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

    specializations: list[int] | None = None

    @field_validator("specializations", mode="before")
    @classmethod
    def specializations_str_validation(cls, value: str | list[int]) -> list[int] | None:
        if not isinstance(value, str):
            return value
        if value == "":
            return []
        try:
            new_value = [int(value) for value in value.replace(" ", "").split(",")]
            return new_value
        except ValueError as exc:
            raise ValueError(
                'Для передачи строки с числами в поле specializations используйте формат: "1, 2, 3"'
            ) from exc


class ExternalSiteUserRequest(BaseExternalSiteUser):
    """Класс схемы запроса для ExternalSiteUser."""

    user_id: int = Field(..., gt=0)
    id_hash: str = Field(..., min_length=1, max_length=256)
    first_name: str = Field(..., max_length=64)
    last_name: str = Field(..., max_length=64)
    email: EmailStr = Field(..., max_length=48)
    moderation_status: str = Field(...)

    def to_orm(self) -> ExternalSiteUser:
        return ExternalSiteUser(
            external_id=self.user_id,
            id_hash=self.id_hash,
            first_name=self.first_name,
            last_name=self.last_name,
            email=self.email,
            moderation_status=self.moderation_status,
        )


class ExternalSiteVolunteerRequest(ExternalSiteUserRequest, BaseExternalSiteUserVolunteer):
    """Класс схемы запроса для ExternalSiteUser (Volunteer)."""

    specializations: list[int]

    def to_orm(self) -> ExternalSiteUser:
        user_orm = super().to_orm()
        user_orm.role = UserRoles.VOLUNTEER
        user_orm.specializations = self.specializations
        return user_orm


class ExternalSiteFundRequest(ExternalSiteUserRequest):
    """Класс схемы запроса для ExternalSiteUser (Fund)."""

    def to_orm(self) -> ExternalSiteUser:
        user_orm = super().to_orm()
        user_orm.role = UserRoles.FUND
        user_orm.specializations = None
        return user_orm


class ExternalSiteVolunteerPartialUpdate(BaseExternalSiteUser, BaseExternalSiteUserVolunteer):
    """Класс схемы обновления для ExternalSiteUser (Volunteer)."""

    pass


class ExternalSiteFundPartialUpdate(BaseExternalSiteUser):
    """Класс схемы обновления для ExternalSiteUser (Fund)."""

    pass
