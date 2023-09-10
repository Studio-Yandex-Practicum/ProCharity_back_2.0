from dependency_injector import containers, providers
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.api.services import CategoryService, ExternalSiteUserService, TaskService
from src.api.services.admin_service import AdminService
from src.api.services.analytics import AnalyticsService
from src.api.services.health_check import HealthCheckService
from src.api.services.messages import TelegramNotificationService
from src.bot.bot import create_bot
from src.bot.services.unsubscribe_reason import UnsubscribeReasonService
from src.core.db import get_session
from src.core.db.repository.admin_repository import AdminUserRepository
from src.core.db.repository.category import CategoryRepository
from src.core.db.repository.external_site_user import ExternalSiteUserRepository
from src.core.db.repository.task import TaskRepository
from src.core.db.repository.unsubscribe_reason import UnsubscribeReasonRepository
from src.core.db.repository.user import UserRepository
from src.settings import get_settings


class Container(containers.DeclarativeContainer):
    """Контейнер dependency_injector."""

    # Settings
    settings = providers.Singleton(get_settings)

    # Database connection
    engine = providers.Singleton(create_async_engine, url=settings.provided.database_url)
    sessionmaker = providers.Singleton(async_sessionmaker, bind=engine, expire_on_commit=False)
    session = providers.Resource(get_session, sessionmaker=sessionmaker)
    admin_repository = providers.Factory(AdminUserRepository, session=session)
    admin_service = providers.Factory(AdminService, admin_repository=admin_repository)

    # Applications
    fastapi_app = providers.Singleton(FastAPI, debug=settings.provided.DEBUG)
    telegram_bot = providers.Singleton(create_bot, bot_token=settings.provided.BOT_TOKEN)

    # Repositories:
    user_repository = providers.Factory(UserRepository, session=session)
    site_user_repository = providers.Factory(ExternalSiteUserRepository, session=session)
    category_repository = providers.Factory(CategoryRepository, session=session)
    task_repository = providers.Factory(TaskRepository, session=session)
    unsubscribe_reason_repository = providers.Factory(UnsubscribeReasonRepository, session=session)

    # API services:
    site_user_service = providers.Factory(
        ExternalSiteUserService, site_user_repository=site_user_repository, session=session
    )
    category_service = providers.Factory(CategoryService, category_repository=category_repository, session=session)
    task_service = providers.Factory(TaskService, task_repository=task_repository, session=session)
    message_service = providers.Factory(TelegramNotificationService, telegram_bot=telegram_bot, session=session)
    analytic_service = providers.Factory(AnalyticsService, user_repository=user_repository)
    health_check_service = providers.Factory(
        HealthCheckService, task_repository=task_repository, telegram_bot=telegram_bot
    )
    unsubscribe_reason_service = providers.Factory(
        UnsubscribeReasonService,
        unsubscribe_reason_repository=unsubscribe_reason_repository, user_repository=user_repository
    )
