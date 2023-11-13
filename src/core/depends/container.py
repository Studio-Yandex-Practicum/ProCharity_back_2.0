from dependency_injector import containers, providers

from src.core.depends.api_services import APIServicesContainer
from src.core.depends.applications import ApplicationsContainer
from src.core.depends.bot_services import BotServicesContainer
from src.core.depends.data_base_connection import DataBaseConnectionContainer
from src.core.depends.jwt_services import JWTServicesContainer
from src.core.depends.repositories import RepositoriesContainer
from src.settings import get_settings


class Container(containers.DeclarativeContainer):
    """Главный контейнер приложения."""

    settings = providers.Singleton(get_settings)
    database_connection_container = providers.Container(DataBaseConnectionContainer, settings=settings)
    applications_container = providers.Container(ApplicationsContainer, settings=settings)
    repositories_container = providers.Container(
        RepositoriesContainer, data_base_connection=database_connection_container
    )
    api_services_container = providers.Container(
        APIServicesContainer,
        repositories=repositories_container,
        data_base_connection=database_connection_container,
        applications=applications_container,
    )
    bot_services_container = providers.Container(BotServicesContainer, repositories=repositories_container)
    jwt_services_container = providers.Container(JWTServicesContainer, settings=settings)
