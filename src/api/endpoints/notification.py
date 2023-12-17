import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import InfoRate, MessageList, TelegramNotificationRequest, TelegramNotificationUsersRequest
from src.api.services.messages import TelegramNotificationService
from src.core.depends import Container
from src.core.exceptions.exceptions import SendMessageError

notification_router = APIRouter(dependencies=[Depends(check_header_contains_token)])
log = structlog.get_logger()


@notification_router.post(
    "/",
    response_model=InfoRate,
    description="Сообщение для группы пользователей",
)
@inject
async def send_telegram_notification(
    notifications: TelegramNotificationUsersRequest,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    """Отправляет сообщение указанной группе пользователей"""
    result = await telegram_notification_service.send_messages_to_group_of_users(notifications)
    rate = InfoRate()
    rate = telegram_notification_service.collect_respond_and_status(result, rate)
    return rate


@notification_router.post(
    "/group",
    response_model=InfoRate,
    description="Отправить сообщения для разных пользователей по user_id",
)
@inject
async def send_messages_to_group_of_users(
    message_list: MessageList,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    """
    Отправляет сообщения для разных пользователей по user_id
    :param message_list: Список сообщений
    :param telegram_notification_service: Сервис для отправки сообщений
    :return: Количество успешных и неуспешных отправок
    """
    rate = InfoRate()
    await log.ainfo("Начало отправки сообщений для группы пользователей")
    for message in message_list.messages:
        try:
            status, response = await telegram_notification_service.send_message_to_user_by_user_id(message.user_id, message)
            rate = telegram_notification_service.count_rate(status, response, rate)
        except SendMessageError as e:
            await log.ainfo(e)
            status, error_message, error_type = False, e.error_message, e.error_type
            rate = telegram_notification_service.count_rate(status, error_message, rate, error_type)

    await log.ainfo("Конец отправки сообщений для группы пользователей")
    return rate


@notification_router.post(
    "/{telegram_id}",
    response_model=InfoRate,
    description="Отправляет сообщение определенному пользователю.",
)
@inject
async def send_user_message(
    telegram_id: int,
    notifications: TelegramNotificationRequest,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    rate = InfoRate()
    status, notifications.message = await telegram_notification_service.send_message_to_user(telegram_id, notifications)
    rate = telegram_notification_service.count_rate(status, notifications.message, rate)
    return rate
