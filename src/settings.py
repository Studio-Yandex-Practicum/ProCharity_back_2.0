import uuid
from functools import lru_cache
from pathlib import Path
from typing import Annotated
from urllib.parse import urljoin

from pydantic import AnyHttpUrl, BeforeValidator, EmailStr, TypeAdapter, field_validator, validator
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

Url = Annotated[str, BeforeValidator(lambda value: str(TypeAdapter(AnyHttpUrl).validate_python(value)))]


@lru_cache
def get_env_path() -> Path | None:
    import importlib

    try:
        importlib.import_module("dotenv")
    except ImportError:
        return
    if Path.exists(BASE_DIR / ".env"):
        return BASE_DIR / ".env"


class Settings(BaseSettings):
    """Настройки проекта."""

    APPLICATION_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "secret_key"
    ROOT_PATH: str = "/api"
    DEBUG: bool = False
    USE_NGROK: bool = False
    STATIC_DIR: str | Path = BASE_DIR / "templates/"
    STATIC_URL: str = "static/"

    # Токен доступа к API
    ACCESS_TOKEN_FOR_PROCHARITY: str = ""

    # Параметры подключения к БД
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # Настройки бота
    BOT_TOKEN: str
    BOT_WEBHOOK_MODE: bool = False
    TELEGRAM_SECRET_TOKEN: str = str(uuid.uuid4())

    # Настройки jwt
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str | Path = BASE_DIR / "logs"
    LOG_FILE: str = "app.log"
    LOG_FILE_SIZE: int = 10 * 2**20
    LOG_FILES_TO_KEEP: int = 5

    # Organization data
    ORGANIZATIONS_EMAIL: EmailStr

    # Настройки отправки сообщений через электронную почту
    MAIL_SERVER: str = ""
    MAIL_PORT: int = 465
    MAIL_LOGIN: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    # Директория с шаблонами электронной почты
    EMAIL_TEMPLATE_DIRECTORY: Path = BASE_DIR / "templates" / "email"

    # Адреса электронной почты администраторов
    EMAIL_ADMIN: EmailStr

    # Время жизни токена
    TOKEN_EXPIRATION: int = 60 * 60 * 24

    # Настройки получения коммитов
    LAST_COMMIT: str = ""
    COMMIT_DATE: str = ""
    TAGS: list[str] = []

    # URLs проекта Procharity
    PROCHARITY_URL: Url = "https://procharity.ru"
    YA_PRAKTIKUM_URL: Url = "https://praktikum.yandex.ru/"
    HELP_PROCHARITY_URL: Url = "https://help.procharity.ru/"

    @field_validator("PROCHARITY_URL", "HELP_PROCHARITY_URL")
    def check_last_slash_url(cls, v) -> str:
        """Кастомный валидатор-добавлятор последнего слэша в константе URL."""

        if v[-1] != "/":
            return urljoin(v, "/")
        return v

    @validator("APPLICATION_URL")
    def check_domain_startswith_https_or_add_https(cls, v) -> str:
        """Добавить 'https://' к домену."""
        if "https://" in v or "http://" in v:
            return v
        return urljoin("https://", f"//{v}")

    @property
    def database_url(self) -> str:
        """Получить ссылку для подключения к DB."""
        return (
            "postgresql+asyncpg://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def api_url(self) -> str:
        return urljoin(self.APPLICATION_URL, self.ROOT_PATH + "/")

    @property
    def static_url(self) -> str:
        return urljoin(self.APPLICATION_URL, settings.STATIC_URL)

    @property
    def telegram_webhook_url(self) -> str:
        """Получить url-ссылку на эндпоинт для работы telegram в режиме webhook."""
        return urljoin(self.api_url, "telegram/webhook")

    @property
    def feedback_form_template_url(self) -> str:
        """Получить url-ссылку на HTML шаблон формы обратной связи."""
        return urljoin(self.static_url, "feedback_form/feedback_form.html")

    @property
    def procharity_registration_url(self) -> str:
        """Получить url-ссылку на страницу регистрации."""
        return urljoin(self.PROCHARITY_URL, "registration/")

    @property
    def procharity_volunteer_auth_url(self) -> str:
        """Получить url-ссылку на страницу авторизации волонтёра."""
        return urljoin(self.PROCHARITY_URL, "volunteers/settings/")

    @property
    def procharity_faq_volunteer_url(self) -> str:
        """Получить url-ссылку на страницу базы знаний."""
        return urljoin(self.HELP_PROCHARITY_URL, "category/1876")

    @property
    def procharity_bonus_info_url(self) -> str:
        """Получить url-ссылку на страницу с информацией о бонусах."""
        return urljoin(self.HELP_PROCHARITY_URL, "article/6646")


@lru_cache()
def get_settings():
    return Settings(_env_file=get_env_path())  # type: ignore


settings = get_settings()
