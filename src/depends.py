from datetime import timedelta

from dependency_injector import containers, providers
from fastapi import FastAPI
from fastapi_jwt import JwtAccessBearerCookie, JwtRefreshBearer
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

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

    # BOT services:
    bot_category_service = providers.Factory(BotCategoryService, category_repository=category_repository)
    bot_user_service = providers.Factory(BotUserService, user_repository=user_repository)
    bot_task_service = providers.Factory(
        BotTaskService,
        task_repository=task_repository,
        user_repository=user_repository,
    )
    bot_site_user_service = providers.Factory(BotExternalSiteUserService, site_user_repository=site_user_repository)
    unsubscribe_reason_service = providers.Factory(
        UnsubscribeReasonService,
        unsubscribe_reason_repository=unsubscribe_reason_repository,
        user_repository=user_repository,
    )

    # JWT services:
    access_security = providers.Factory(
        JwtAccessBearerCookie,
        secret_key=settings.provided.SECRET_KEY,
        auto_error=False,
        access_expires_delta=timedelta(hours=1),
    )
    refresh_security = providers.Factory(JwtRefreshBearer, secret_key=settings.provided.SECRET_KEY, auto_error=True)
