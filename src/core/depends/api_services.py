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


class APIServicesContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей API Service."""

    repositories = providers.DependenciesContainer()
    data_base_connection = providers.DependenciesContainer()
    applications = providers.DependenciesContainer()
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
        user_repository=repositories.user_repository,
    )
    analytic_service = providers.Factory(
        AnalyticsService,
        user_repository=repositories.user_repository,
        unsubscribe_reason_repository=repositories.unsubscribe_reason_repository,
    )
    health_check_service = providers.Factory(
        HealthCheckService,
        task_repository=repositories.task_repository,
        telegram_bot=applications.telegram_bot,
    )
