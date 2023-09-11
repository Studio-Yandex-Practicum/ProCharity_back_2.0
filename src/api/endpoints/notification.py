import logging

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from src.api.schemas import (
    Message, MessageList,
    TelegramNotificationRequest,
    TelegramNotificationUsersRequest
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


def get_logger():
    logger = logging.getLogger("send_to_group_logger")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger

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
        logger: logging.Logger = Depends(get_logger)
):
    logger.info("Sending messages to group")
    SUCCESSFUL_COUNT = 0
    UNSUCCESSFUL_COUNT = 0

    for message in message_list.messages:
        respond = await telegram_notification_service.send_message_to_user(
            message.telegram_id,
            message
        )
        if respond:
            SUCCESSFUL_COUNT += 1
        else:
            UNSUCCESSFUL_COUNT += 1
    result = (f'Successful sending - {SUCCESSFUL_COUNT}, '
              f'Unsuccessful sending - {UNSUCCESSFUL_COUNT}')
    logger.info(result)
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
