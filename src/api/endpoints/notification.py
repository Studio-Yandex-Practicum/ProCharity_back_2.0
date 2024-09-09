import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.auth import check_header_contains_token
from src.api.schemas import (
    InfoRate,
    MessageList,
    TelegramNotificationByFilterRequest,
    TelegramNotificationRequest,
    TelegramNotificationUsersRequest,
)
from src.api.services import TelegramNotificationService
from src.core.depends import Container

notification_router_by_token = APIRouter(prefix="/messages", dependencies=[Depends(check_header_contains_token)])
notification_router_by_admin = APIRouter()
messages_router_by_admin = APIRouter(prefix="/messages")

log = structlog.get_logger()


@notification_router_by_admin.post(
    "/send_telegram_notification",
    description="Отправляет сообщение пользователям, соответствующим заданному критерию.",
)
@inject
async def send_message(
    notification: TelegramNotificationUsersRequest,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    filters = dict(has_mailing=notification.mode.to_bool_or_none(), banned=False)
    results = await telegram_notification_service.send_message_to_users_by_filters(filters, notification.message)
    return InfoRate.from_results(results)


@messages_router_by_admin.post(
    "/new",
    description="Отправляет сообщение пользователям, соответствующим заданным критериям.",
)
@inject
async def send_message_to_users_by_filters(
    notification: TelegramNotificationByFilterRequest,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    filters = notification.mode.model_dump()
    filters.update(banned=False)
    results = await telegram_notification_service.send_message_to_users_by_filters(filters, notification.message)
    return InfoRate.from_results(results)


@notification_router_by_token.post(
    "/group",
    description="Отправляет сообщения различным пользователям.",
)
@inject
async def send_messages_to_users(
    message_list: MessageList,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    await log.ainfo("Начало отправки сообщений для группы пользователей")
    results = (
        await telegram_notification_service.send_message_to_user_by_id_hash(message.id_hash, message.message)
        for message in message_list.messages
    )
    response = await InfoRate.from_results_async(results)
    await log.ainfo("Конец отправки сообщений для группы пользователей")
    return response


@messages_router_by_admin.post(
    "/{telegram_id}",
    description="Отправляет сообщение заданному пользователю.",
)
@inject
async def send_message_to_user(
    telegram_id: int,
    notification: TelegramNotificationRequest,
    telegram_notification_service: TelegramNotificationService = Depends(
        Provide[Container.api_services_container.message_service]
    ),
) -> InfoRate:
    result = await telegram_notification_service.send_message_by_telegram_id(telegram_id, notification.message)
    return InfoRate.from_results([result])
