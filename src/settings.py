from pathlib import Path
from urllib.parse import urljoin

from pydantic import BaseSettings, validator
from pydantic.tools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = None
if Path.exists(BASE_DIR / ".env"):
    ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Настройки проекта."""

    APPLICATION_URL: str = "localhost"
    SECRET_KEY: str 
    ROOT_PATH: str = "/api/"
    DEBUG: bool = False

    # Параметры подключения к БД
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    DB_HOST: str
    DB_PORT: str

    # Настройки бота
    BOT_TOKEN: str
    BOT_WEBHOOK_MODE: bool = False

    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str | Path = BASE_DIR / "logs"
    LOG_FILE: str = "app.log"
    LOG_LEVEL: str = "INFO"
    LOG_FILE_SIZE: int = 10 * 2**20
    LOG_FILES_TO_KEEP: int = 5

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
        return urljoin(self.APPLICATION_URL, self.ROOT_PATH)

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
        env_file = ENV_FILE


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
