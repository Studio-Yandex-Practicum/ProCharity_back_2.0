from fastapi import APIRouter, Depends

from src.api.schemas import TelegramNotificationRequest, TelegramNotificationUsersRequest
from src.api.services.messages import TelegramNotificationService

notification_router = APIRouter()


@notification_router.post(
    "/",
    description="Сообщение для группы пользователей",
)
async def send_telegram_notification(
    notifications: TelegramNotificationUsersRequest,
    telegram_notification_service: TelegramNotificationService = Depends(),
) -> None:
    """Отправляет сообщение указаной группе пользователей"""
    await telegram_notification_service.send_messages_to_group_of_users(notifications)


@notification_router.post(
    "/{telegram_id}",
    response_model=str,
    description="Отправляет сообщение определенному пользователю.",
)
async def send_user_message(
    telegram_id: int,
    notifications: TelegramNotificationRequest,
    telegram_notification_service: TelegramNotificationService = Depends(),
) -> str:
    await telegram_notification_service.send_message_to_user(telegram_id, notifications)
    return notifications.message
