from dependency_injector import containers, providers

from src.core.services import EmailProvider, ProcharityAPI, TechMessageService, TelegramNotification


class CoreServicesContainer(containers.DeclarativeContainer):
    repositories = providers.DependenciesContainer()

    sessionmaker = providers.Dependency()
    settings = providers.Dependency()
    telegram_bot = providers.Dependency()

    email_provider = providers.Factory(EmailProvider, sessionmaker=sessionmaker, settings=settings)
    telegram_notification = providers.Factory(TelegramNotification, telegram_bot=telegram_bot)
    tech_message = providers.Factory(TechMessageService, repository=repositories.tech_message_repository)
    procharity_api = providers.Factory(
        ProcharityAPI, settings=settings, email_provider=email_provider, tech_message_service=tech_message
    )
