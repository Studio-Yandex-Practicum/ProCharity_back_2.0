import os
from pathlib import Path
from urllib.parse import urljoin

from pydantic import BaseSettings
from pydantic.tools import lru_cache

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if os.path.exists(str(BASE_DIR / ".env")):
    ENV_FILE = ".env"
else:
    ENV_FILE = ".env.example"


class Settings(BaseSettings):
    """Настройки проекта."""

    APPLICATION_URL: str
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
    LOG_LOCATION = BASE_DIR / "logs/{time}.log"
    LOG_ROTATION = "5 MB"
    LOG_RETENTION = 10
    LOG_COMPRESSION = "tar.gz"
    LOG_LEVEL = "WARNING"

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

    class Config:
        env_file = ENV_FILE


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
