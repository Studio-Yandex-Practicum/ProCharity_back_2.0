from dependency_injector import containers, providers

from src.api.services import (
    AdminService,
    AnalyticsService,
    CategoryService,
    ExternalSiteUserService,
    HealthCheckService,
    TaskService,
    TelegramNotificationService,
)
from src.core.depends.applications import ApplicationsContainer
from src.core.depends.data_base_connection import DataBaseConnectionContainer
from src.core.depends.repositories import RepositoriesContainer


class APIServicesContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей API Service."""

    repositories = providers.Container(RepositoriesContainer)
    data_base_connection = providers.Container(DataBaseConnectionContainer)
    applications = providers.Container(ApplicationsContainer)
    admin_service = providers.Factory(
        AdminService,
        admin_repository=repositories.admin_repository,
    )
    site_user_service = providers.Factory(
        ExternalSiteUserService,
        site_user_repository=repositories.site_user_repository,
        session=data_base_connection.session,
    )
    category_service = providers.Factory(
        CategoryService,
        category_repository=repositories.category_repository,
        session=data_base_connection.session,
    )
    task_service = providers.Factory(
        TaskService,
        task_repository=repositories.task_repository,
        session=data_base_connection.session,
    )
    message_service = providers.Factory(
        TelegramNotificationService,
        telegram_bot=applications.telegram_bot,
        session=data_base_connection.session,
    )
    analytic_service = providers.Factory(
        AnalyticsService,
        user_repository=repositories.user_repository,
    )
    health_check_service = providers.Factory(
        HealthCheckService,
        task_repository=repositories.task_repository,
        telegram_bot=applications.telegram_bot,
    )
