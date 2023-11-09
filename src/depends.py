from datetime import timedelta

from dependency_injector import containers, providers
from fastapi import FastAPI
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.main import init_fastapi
from src.api.services import (
    AdminService,
    AnalyticsService,
    CategoryService,
    ExternalSiteUserService,
    HealthCheckService,
    TaskService,
    TelegramNotificationService,
)
from src.bot.bot import create_bot
from src.bot.main import init_bot
from src.bot.services import UnsubscribeReasonService
from src.bot.services.category import CategoryService as BotCategoryService
from src.bot.services.external_site_user import ExternalSiteUserService as BotExternalSiteUserService
from src.bot.services.task import TaskService as BotTaskService
from src.bot.services.user import UserService as BotUserService
from src.core.db import get_session
from src.core.db.repository import (
    AdminUserRepository,
    CategoryRepository,
    ExternalSiteUserRepository,
    TaskRepository,
    UnsubscribeReasonRepository,
    UserRepository,
)
from src.settings import get_settings


class SettingsContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Settings."""

    settings = providers.Singleton(get_settings)


class DataBaseConnectionContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей DataBase connection."""

    settings = providers.Container(SettingsContainer)
    engine = providers.Singleton(
        create_async_engine,
        url=settings.settings.provided.database_url,
    )
    sessionmaker = providers.Singleton(
        async_sessionmaker,
        bind=engine,
        expire_on_commit=False,
    )
    session = providers.Resource(
        get_session,
        sessionmaker=sessionmaker,
    )


class ApplicationsContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Applications."""

    settings = providers.Container(SettingsContainer)
    telegram_bot = providers.Singleton(
        init_bot,
        telegram_bot=providers.Singleton(
            create_bot,
            bot_token=settings.settings.provided.BOT_TOKEN,
        ),
    )
    fastapi_app = providers.Singleton(
        init_fastapi,
        fastapi_app=providers.Singleton(FastAPI, debug=settings.settings.provided.DEBUG),
        settings=settings.settings,
    )


class RepositoriesContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Repositories."""

    data_base_connection = providers.Container(DataBaseConnectionContainer)
    user_repository = providers.Factory(
        UserRepository,
        session=data_base_connection.session,
    )
    site_user_repository = providers.Factory(
        ExternalSiteUserRepository,
        session=data_base_connection.session,
    )
    category_repository = providers.Factory(
        CategoryRepository,
        session=data_base_connection.session,
    )
    task_repository = providers.Factory(
        TaskRepository,
        session=data_base_connection.session,
    )
    unsubscribe_reason_repository = providers.Factory(
        UnsubscribeReasonRepository,
        session=data_base_connection.session,
    )
    admin_repository = providers.Factory(
        AdminUserRepository,
        session=data_base_connection.session,
    )


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


class BotServicesContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Bot services."""

    repositories = providers.Container(RepositoriesContainer)
    bot_category_service = providers.Factory(
        BotCategoryService,
        category_repository=repositories.category_repository,
    )
    bot_user_service = providers.Factory(
        BotUserService,
        user_repository=repositories.user_repository,
    )
    bot_task_service = providers.Factory(
        BotTaskService,
        task_repository=repositories.task_repository,
        user_repository=repositories.user_repository,
    )
    bot_site_user_service = providers.Factory(
        BotExternalSiteUserService,
        site_user_repository=repositories.site_user_repository,
    )
    unsubscribe_reason_service = providers.Factory(
        UnsubscribeReasonService,
        unsubscribe_reason_repository=repositories.unsubscribe_reason_repository,
        user_repository=repositories.user_repository,
    )


class JWTServicesContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей JWT services."""

    settings = providers.DependenciesContainer()
    access_security = providers.Factory(
        JwtAccessBearerCookie,
        secret_key=settings.SECRET_KEY,
        auto_error=False,
        access_expires_delta=timedelta(hours=1),
    )
    refresh_security = providers.Factory(
        JwtRefreshBearer,
        secret_key=settings.SECRET_KEY,
        auto_error=True,
    )


class Container(containers.DeclarativeContainer):
    """Главный контейнер приложения."""

    settings_container = providers.Container(SettingsContainer)
    database_connection_container = providers.Container(DataBaseConnectionContainer)
    applications_container = providers.Container(ApplicationsContainer)
    repositories_container = providers.Container(RepositoriesContainer)
    api_services_container = providers.Container(APIServicesContainer)
    bot_services_container = providers.Container(BotServicesContainer)
    jwt_services_container = providers.Container(JWTServicesContainer)
