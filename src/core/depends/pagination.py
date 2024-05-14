from dependency_injector import containers, providers

from src.api.pagination import UserPaginator


class PaginateContainer(containers.DeclarativeContainer):
    """Контейнер зависимостей Paginate."""

    repositories = providers.DependenciesContainer()

    user_paginate = providers.Factory(
        UserPaginator,
        user_repository=repositories.user_repository,
    )
