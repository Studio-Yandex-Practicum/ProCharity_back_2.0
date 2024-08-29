from dependency_injector import containers, providers

from src.api.pagination import AdminUserPaginator, TechMessagePaginator, UserPaginator


class PaginateContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Paginate."""

    repositories = providers.DependenciesContainer()

    user_paginate = providers.Factory(
        UserPaginator,
        user_repository=repositories.user_repository,
    )

    admin_user_paginate = providers.Factory(
        AdminUserPaginator,
        repository=repositories.admin_repository,
    )

    tech_message_paginate = providers.Factory(
        TechMessagePaginator,
        repository=repositories.tech_message_repository,
    )
