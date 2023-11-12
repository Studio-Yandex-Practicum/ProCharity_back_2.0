from dependency_injector import containers, providers

from src.settings import get_settings


class SettingsContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Settings."""

    settings = providers.Singleton(get_settings)
