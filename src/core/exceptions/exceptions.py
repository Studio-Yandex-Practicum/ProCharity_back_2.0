from http import HTTPStatus
from typing import Any

from starlette.exceptions import HTTPException

from src.core.db.models import Base as DatabaseModel


class ApplicationException(HTTPException):
    status_code: int = None
    detail: str = None
    headers: dict[str, Any] = None

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail, headers=self.headers)


class NotFoundException(ApplicationException):
    def __init__(self, object_name: str, object_id: int):
        self.status_code = HTTPStatus.NOT_FOUND
        self.detail = f"Объект {object_name} с id: {object_id} не найден"


class AlreadyExistsException(ApplicationException):
    def __init__(self, obj: DatabaseModel):
        self.status_code = HTTPStatus.BAD_REQUEST
        self.detail = f"Объект {obj} уже существует"
