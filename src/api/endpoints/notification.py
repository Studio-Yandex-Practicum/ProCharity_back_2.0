import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.permissions import is_active_user
from src.api.schemas import InfoRate, MessageList, TelegramNotificationRequest, TelegramNotificationUsersRequest
from src.api.services.messages import TelegramNotificationService
from src.core.depends import Container

notification_router_by_token = APIRouter(dependencies=[Depends(check_header_contains_token)])
notification_router_by_admin = APIRouter(dependencies=[Depends(is_active_user)])

log = structlog.get_logger()


@notification_router_by_admin.post(
    "",
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
    result = await telegram_notification_service.send_messages_to_filtered_users(notifications)
    rate = InfoRate()
    rate = telegram_notification_service.collect_respond_and_status(result, rate)
    return rate


@notification_router_by_token.post(
    "/group",
    description="Сообщения для разных пользователей",
)
@inject
async def send_messages_to_group_of_users(
    message_list: MessageList,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    await log.ainfo("Начало отправки сообщений для группы пользователей")
    rate = InfoRate()
    for message in message_list.messages:
        status, msg = await telegram_notification_service.send_message_to_user_by_id_hash(
            message.id_hash, message.message
        )
        rate = telegram_notification_service.count_rate(status, msg, rate)
    await log.ainfo("Конец отправки сообщений для группы пользователей")
    return rate


@notification_router_by_admin.post(
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
    status, notifications.message = await telegram_notification_service.send_message_by_telegram_id(
        telegram_id, notifications.message
    )
    rate = telegram_notification_service.count_rate(status, notifications.message, rate)
    return rate
