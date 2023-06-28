from fastapi import APIRouter, Depends
from src.api.schemas import TelegramNotificationRequest
from src.api.services.messages import TelegramNotificationService


users_group_notification_router = APIRouter()


@users_group_notification_router.post(
    "/",
    description="Сообщение для группы пользователей",
)
async def send_telegram_notification(
    notifications: TelegramNotificationRequest,
    telegram_notification_service: TelegramNotificationService = Depends(),
) -> None:
    """Отправляет сообщение указаной группе пользователей"""
    await telegram_notification_service.send_messages_to_group_of_users(notifications)
