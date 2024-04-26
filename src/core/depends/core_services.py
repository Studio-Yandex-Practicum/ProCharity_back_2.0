from dependency_injector import containers, providers

from src.core.services import EmailProvider, ProcharityAPI, TelegramNotification


class CoreServicesContainer(containers.DeclarativeContainer):
    sessionmaker = providers.Dependency()
    settings = providers.Dependency()
    telegram_bot = providers.Dependency()

    email_provider = providers.Factory(EmailProvider, sessionmaker=sessionmaker, settings=settings)
    telegram_notification = providers.Factory(TelegramNotification, telegram_bot=telegram_bot)
    procharity_api = providers.Factory(ProcharityAPI, settings=settings)
