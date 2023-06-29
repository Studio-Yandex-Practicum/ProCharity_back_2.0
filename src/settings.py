from pathlib import Path
from urllib.parse import urljoin

from pydantic import BaseSettings, validator
from pydantic.tools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent


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

    APPLICATION_URL: str = "localhost"
    SECRET_KEY: str = "secret_key"
    ROOT_PATH: str = "/api"
    DEBUG: bool = False
    USE_NGROK: bool = False

    # Параметры подключения к БД
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # Настройки бота
    BOT_TOKEN: str
    BOT_WEBHOOK_MODE: bool = False

    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str | Path = BASE_DIR / "logs"
    LOG_FILE: str = "app.log"
    LOG_FILE_SIZE: int = 10 * 2**20
    LOG_FILES_TO_KEEP: int = 5

    # Organization data
    ORGANIZATIONS_EMAIL: str = "procharity@yandex.ru"

    # Настройки отправки сообщений через электронную почту
    MAIL_SERVER: str = "smtp.yandex.ru"  # адрес почтового сервиса
    MAIL_PORT: int = 465  # порт для подключения к почтовому сервису
    MAIL_LOGIN: str = ""  # логин для подключения к почтовому сервису
    MAIL_PASSWORD: str = ""  # пароль для подключения к почтовому сервису
    MAIL_STARTTLS: bool = False  # использовать STARTTLS или нет
    MAIL_SSL_TLS: bool = True  # использовать SSL/TLS или нет
    USE_CREDENTIALS: bool = True  # использовать логин/пароль для подключения к почтовому серверу или нет
    VALIDATE_CERTS: bool = True  # проверять SSL сертификат почтового сервера или нет

    # Адреса электронной почты администраторов
    EMAIL_ADMIN = ["procharity.admin_1@yandex.ru"]

    @validator("APPLICATION_URL")
    def check_domain_startswith_https_or_add_https(cls, v) -> str:
        """Добавить 'https://' к домену."""
        if "https://" in v:
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
    def telegram_webhook_url(self) -> str:
        """Получить url-ссылку на эндпоинт для работы telegram в режиме webhook."""
        return urljoin(self.api_url, "telegram/webhook")

    @property
    def feedback_form_template_url(self) -> str:
        """Получить url-ссылку на HTML шаблон формы обратной связи."""
        return urljoin(self.api_url, "telegram/feedback-form")

    @property
    def feedback_form_template(self) -> Path:
        """Получить HTML-шаблон формы обратной связи."""
        return BASE_DIR / "src" / "bot" / "templates" / "feedback_form.html"

    class Config:
        env_file = get_env_path()


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
