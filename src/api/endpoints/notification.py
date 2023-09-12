import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import (
    Message, MessageList,
    TelegramNotificationRequest,
    TelegramNotificationUsersRequest,
)
from src.api.services.messages import TelegramNotificationService
from src.depends import Container


notification_router = APIRouter()

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
    description="Сообщение для группы пользователей",
)
@inject
async def send_messages_to_group_of_users(
        message_list: MessageList,
        telegram_notification_service: TelegramNotificationService = Depends(
            Provide[Container.message_service]
        ),
):
    successful_rate = 0
    unsuccessful_rate = 0

    for message in message_list.messages:
        respond = await telegram_notification_service.send_message_to_user(
            message.telegram_id,
            message
        )
        d = respond
        d = telegram_notification_service
        if respond:
            successful_rate += 1
        else:
            unsuccessful_rate += 1
    result = (f'Successful sending - {successful_rate}, '
              f'Unsuccessful sending - {unsuccessful_rate}')
    return (message_list, result)


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
