from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_DB: str

    class Config:
        env_file = ".env"


settings = Settings()
print(settings.POSTGRES_DB)
