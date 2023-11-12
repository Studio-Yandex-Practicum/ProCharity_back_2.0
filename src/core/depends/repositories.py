from dependency_injector import containers, providers

from src.core.db.repository import (
    AdminUserRepository,
    CategoryRepository,
    ExternalSiteUserRepository,
    TaskRepository,
    UnsubscribeReasonRepository,
    UserRepository,
)
from src.core.depends.data_base_connection import DataBaseConnectionContainer


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
