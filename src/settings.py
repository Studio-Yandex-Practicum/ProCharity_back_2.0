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

    APPLICATION_URL: str = "http://localhost:8000"
    SECRET_KEY: str = "secret_key"
    ROOT_PATH: str = "/api"
    DEBUG: bool = False
    USE_NGROK: bool = False
    STATIC_DIR: str | Path = BASE_DIR / "templates/"
    STATIC_URL: str = "static/"

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

    class Config:
        env_file = get_env_path()


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
