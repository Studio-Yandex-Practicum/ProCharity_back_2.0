from dependency_injector import containers, providers

from src.settings import get_settings

from .api_services import APIServicesContainer
from .applications import ApplicationsContainer
from .bot_services import BotServicesContainer
from .core_services import CoreServicesContainer
from .data_base_connection import DataBaseConnectionContainer
from .jwt_services import JWTServicesContainer
from .pagination import PaginateContainer
from .repositories import RepositoriesContainer


class Container(containers.DeclarativeContainer):
    """Главный контейнер приложения."""

    settings = providers.Singleton(get_settings)

    database_connection_container = providers.Container(DataBaseConnectionContainer, settings=settings)

    applications_container = providers.Container(ApplicationsContainer, settings=settings)

    repositories_container = providers.Container(
        RepositoriesContainer, data_base_connection=database_connection_container
    )

    core_services_container = providers.Container(
        CoreServicesContainer,
        sessionmaker=database_connection_container.sessionmaker,
        settings=settings,
        telegram_bot=applications_container.telegram_bot,
    )
    api_services_container = providers.Container(
        APIServicesContainer,
        repositories=repositories_container,
        data_base_connection=database_connection_container,
        applications=applications_container,
        telegram_notification=core_services_container.telegram_notification,
    )
    bot_services_container = providers.Container(BotServicesContainer, repositories=repositories_container)

    jwt_services_container = providers.Container(JWTServicesContainer, settings=settings)

    api_paginate_container = providers.Container(PaginateContainer, repositories=repositories_container)
