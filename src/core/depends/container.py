from dependency_injector import containers, providers

from src.core.depends.api_services import APIServicesContainer
from src.core.depends.applications import ApplicationsContainer
from src.core.depends.bot_services import BotServicesContainer
from src.core.depends.data_base_connection import DataBaseConnectionContainer
from src.core.depends.jwt_services import JWTServicesContainer
from src.core.depends.repositories import RepositoriesContainer
from src.core.depends.settings import SettingsContainer


class Container(containers.DeclarativeContainer):
    """Главный контейнер приложения."""

    settings_container = providers.Container(SettingsContainer)
    database_connection_container = providers.Container(DataBaseConnectionContainer)
    applications_container = providers.Container(ApplicationsContainer)
    repositories_container = providers.Container(RepositoriesContainer)
    api_services_container = providers.Container(APIServicesContainer)
    bot_services_container = providers.Container(BotServicesContainer)
    jwt_services_container = providers.Container(JWTServicesContainer)
