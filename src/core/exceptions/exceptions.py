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


class SendMessageError(Exception):
    def __init__(self, user_id, error_message=""):
        super().__init__(error_message)
        self.user_id = user_id
        self.error_message = error_message
        self.error_type = type(self).__name__

    def __str__(self):
        return f"{self.error_type}: {self.error_message}"


class UserNotFoundError(SendMessageError):
    def __init__(self, user_id):
        super().__init__(user_id, "Unable to find the user")


class UserBlockedError(SendMessageError):
    def __init__(self, user_id):
        super().__init__(user_id, "User blocked the bot")


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


class CredentialsException(ApplicationException):
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED
    headers = {"WWW-Authenticate": "Bearer"}

    def __init__(self, detail: str):
        self.detail = detail


class TokenNotProvided(ApplicationException):
    status_code: HTTPStatus = HTTPStatus.UNAUTHORIZED
    detail = "В заголовке запроса не содержится токен."


class InvalidToken(ApplicationException):
    status_code: HTTPStatus = HTTPStatus.FORBIDDEN
    detail = "Токен в заголовке запроса неверный."
