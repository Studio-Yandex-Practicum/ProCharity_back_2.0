from dependency_injector import containers, providers

from src.bot.services import UnsubscribeReasonService
from src.bot.services.category import CategoryService as BotCategoryService
from src.bot.services.external_site_user import ExternalSiteUserService as BotExternalSiteUserService
from src.bot.services.task import TaskService as BotTaskService
from src.bot.services.user import UserService as BotUserService
from src.core.depends.repositories import RepositoriesContainer


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
