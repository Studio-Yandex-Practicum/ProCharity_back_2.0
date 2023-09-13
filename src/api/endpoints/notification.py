import logging

import structlog
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import (
    InfoRate,
    Message,
    MessageList,
    TelegramNotificationRequest,
    TelegramNotificationUsersRequest,
)
from src.api.services.messages import TelegramNotificationService
from src.depends import Container


notification_router = APIRouter()
log = structlog.get_logger()

@notification_router.post(
    "/",
    description="Сообщение для группы пользователей",
)
@inject
async def send_telegram_notification(
    notifications: TelegramNotificationUsersRequest,
    telegram_notification_service: TelegramNotificationService = Depends(Provide[Container.message_service]),
) -> None:
    """Отправляет сообщение указанной группе пользователей"""
    await telegram_notification_service.send_messages_to_group_of_users(notifications)


@notification_router.post(
    "/group",
    response_model=InfoRate,
    description="Сообщение для группы пользователей",
)
@inject
async def send_messages_to_group_of_users(
        message_list: MessageList,
        telegram_notification_service: TelegramNotificationService = Depends(
            Provide[Container.message_service]
        ),
):
    log.info('Начало отправки сообщений для группы пользователей')
    rate = InfoRate()
    for message in message_list.messages:
        respond = await telegram_notification_service.send_message_to_user(
            message.telegram_id,
            message
        )
        rate = telegram_notification_service.count_rate(respond, rate)
    log.info('Конец отправки сообщений для группы пользователей')
    return (rate)


@notification_router.post(
    "/{telegram_id}",
    response_model=str,
    description="Отправляет сообщение определенному пользователю.",
)
@inject
async def send_user_message(
    telegram_id: int,
    notifications: TelegramNotificationRequest,
    telegram_notification_service: TelegramNotificationService = Depends(Provide[Container.message_service]),
) -> str:
    await telegram_notification_service.send_message_to_user(telegram_id, notifications)
    return notifications.message
