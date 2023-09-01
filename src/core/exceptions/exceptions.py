from http import HTTPStatus
from typing import Any

from pydantic import EmailStr
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


class EmailSendError(ApplicationException):
    status_code: HTTPStatus = HTTPStatus.BAD_REQUEST

    def __init__(self, recipients: EmailStr | list[EmailStr], exc: Exception):
        self.detail = f"Возникла ошибка {exc} при отправке email на адрес {recipients}."


class UnauthorizedError(ApplicationException):
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED
    detail = "У Вас нет прав для просмотра запрошенной страницы."


class WebhookOnError(ApplicationException):
    status_code: HTTPStatus = HTTPStatus.NO_CONTENT
    detail = "Telegram Webhook выключен."


class CredentialsException(Exception):
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}
