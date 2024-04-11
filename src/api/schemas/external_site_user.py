from pydantic import Field, field_validator

from src.api.schemas.base import RequestBase
from src.core.db.models import ExternalSiteUser
from src.core.enums import UserRoles


class BaseExternalSiteUserRequest(RequestBase):
    """Базовый класс модели запроса для ExternalSiteUser."""

    user_id: int = Field(...)
    id_hash: str = Field(..., max_length=256)
    first_name: str | None = Field(None, max_length=64)
    last_name: str | None = Field(None, max_length=64)
    email: str = Field(..., max_length=48)

    def to_orm(self) -> ExternalSiteUser:
        return ExternalSiteUser(
            external_id=self.user_id,
            id_hash=self.id_hash,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
        )


class ExternalSiteVolunteerRequest(BaseExternalSiteUserRequest):
    """Класс модели запроса для ExternalSiteUser (Volunteer)."""

    specializations: list[int] | None = None

    def to_orm(self) -> ExternalSiteUser:
        to_orm = super().to_orm()
        to_orm.role = UserRoles.VOLUNTEER
        to_orm.specializations = self.specializations
        return to_orm

    @field_validator("specializations", mode="before")
    def specializations_str_validation(cls, value: str):
        if not isinstance(value, str):
            return value
        try:
            new_value = [int(value) for value in value.replace(" ", "").split(",")]
            return new_value
        except ValueError as exc:
            raise ValueError(
                'Для передачи строки с числами в поле specializations используйте формат: "1, 2, 3"'
            ) from exc


class ExternalSiteFundRequest(BaseExternalSiteUserRequest):
    """Класс модели запроса для ExternalSiteUser (Fund)."""

    def to_orm(self) -> ExternalSiteUser:
        to_orm = super().to_orm()
        to_orm.role = UserRoles.FUND
        return to_orm
