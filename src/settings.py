import uuid
from functools import lru_cache
from pathlib import Path
from typing import Annotated
from urllib.parse import urljoin

from pydantic import AnyHttpUrl, BeforeValidator, EmailStr, TypeAdapter, field_validator
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
    PROCHARITY_API_VERSION: str = "v1"

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

    # Уведомлять ли администратора по почте об ошибках передачи данных из бота
    EMAIL_TO_ADMIN_OF_DATA_TRANSFER_ERROR: bool = False

    # Время жизни токена
    TOKEN_EXPIRATION: int = 60 * 60 * 24

    # Настройки получения коммитов
    LAST_COMMIT: str = ""
    COMMIT_DATE: str = ""
    TAGS: list[str] = []

    # Ключевые поля, изменение которых вызывает рассылку обновленного задания
    # Изменение ключевых полей может потребовать изменения формата сообщения в src.core.messages.display_task()
    TRIGGER_MAILING_FIELDS: list[str] = ["title", "deadline", "category_id", "bonus"]

    # Отображать ли меню для настройки уведомлений
    SHOW_NOTIFICATION_SETTINGS_MENU: bool = False

    # URLs проекта Procharity
    PROCHARITY_URL: Url = "https://procharity.ru"
    HELP_PROCHARITY_URL: Url = "https://help.procharity.ru/"
    ACCESS_TOKEN_SEND_DATA_TO_PROCHARITY: str = ""

    @field_validator("APPLICATION_URL", "PROCHARITY_URL", "HELP_PROCHARITY_URL", "STATIC_URL")
    @classmethod
    def check_last_slash_url(cls, v: str) -> str:
        """Проверить и добавить последний слэш в константе URL."""
        if not v or v[-1] != "/":
            return f"{v}/"
        return v

    @field_validator("ROOT_PATH")
    @classmethod
    def check_prefix_not_ends_with_slash(cls, v: str) -> str:
        """Проверить и убрать слэш в конце префикса для APIRouter."""
        if v and v[-1] == "/":
            return v[:-1]
        return v

    @field_validator("APPLICATION_URL")
    @classmethod
    def check_domain_starts_with_https_or_add_https(cls, v: str) -> str:
        """Добавить 'https://' к домену, если он не содержит протокол."""
        if v.startswith("https://") or v.startswith("http://"):
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
        return urljoin(self.APPLICATION_URL, self.STATIC_URL)

    @property
    def telegram_webhook_url(self) -> str:
        """Получить url-ссылку на эндпоинт для работы telegram в режиме webhook."""
        return urljoin(self.api_url, "telegram/webhook")

    @property
    def feedback_form_template_url(self) -> str:
        """Получить url-ссылку на HTML шаблон формы обратной связи."""
        return urljoin(self.static_url, "feedback_form/feedback_form.html")

    @property
    def procharity_task_url(self) -> str:
        """Получить url-ссылку на страницу с информацией о задании."""
        return urljoin(self.PROCHARITY_URL, "webapp/")

    @property
    def procharity_registration_url(self) -> str:
        """Получить url-ссылку на страницу регистрации."""
        return urljoin(self.PROCHARITY_URL, "registration/")

    @property
    def procharity_volunteer_auth_url(self) -> str:
        """Получить url-ссылку на страницу авторизации волонтёра."""
        return urljoin(self.PROCHARITY_URL, "volunteers/settings/")

    @property
    def procharity_fund_auth_url(self) -> str:
        """Получить url-ссылку на страницу авторизации фонда."""
        return urljoin(self.PROCHARITY_URL, "foundations/lk/settings/")

    @property
    def procharity_volunteer_faq_url(self) -> str:
        """Получить url-ссылку на страницу базы знаний для волонтёров."""
        return urljoin(self.HELP_PROCHARITY_URL, "category/1876")

    @property
    def procharity_fund_faq_url(self) -> str:
        """Получить url-ссылку на страницу базы знаний для фондов."""
        return urljoin(self.HELP_PROCHARITY_URL, "category/1877")

    @property
    def procharity_bonus_info_url(self) -> str:
        """Получить url-ссылку на страницу с информацией о бонусах."""
        return urljoin(self.HELP_PROCHARITY_URL, "article/6646")

    @property
    def procharity_tasks_url(self) -> str:
        """Получить url-ссылку на страницу с заданиями."""
        return urljoin(self.PROCHARITY_URL, "tasks/")

    @property
    def procharity_send_user_categories_api_url(self) -> str:
        """Получить url-ссылку на страницу отправки категорий пользователя."""
        return urljoin(self.PROCHARITY_URL, f"api/{self.PROCHARITY_API_VERSION}/user_categories/")

    @property
    def procharity_send_bot_status_volunteer_api_url(self) -> str:
        """Получить url-ссылку на страницу отправки статуса бота для волонтера."""
        return urljoin(self.PROCHARITY_URL, f"api/{self.PROCHARITY_API_VERSION}/bot_status_volunteer/")

    @property
    def procharity_send_bot_status_fund_api_url(self) -> str:
        """Получить url-ссылку на страницу отправки статуса бота для фонда."""
        return urljoin(self.PROCHARITY_URL, f"api/{self.PROCHARITY_API_VERSION}/bot_status_fund/")

    @property
    def procharity_send_bot_respond_api_url(self) -> str:
        """Получить url-ссылку на страницу отправки статуса отклика на задачу."""
        return urljoin(self.PROCHARITY_URL, f"api/{self.PROCHARITY_API_VERSION}/bot_respond/")


@lru_cache()
def get_settings():
    return Settings(_env_file=get_env_path())  # type: ignore


settings = get_settings()
