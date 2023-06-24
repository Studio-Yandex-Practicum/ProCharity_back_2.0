from fastapi import APIRouter

from src.api.schemas import TelegramMessageRequest
from src.bot import create_bot
from src.core.services.notification import TelegramNotification

notification_router = APIRouter()


@notification_router.post(
    "/{telegram_id}",
    response_model=str,
    description="Отправляет сообщение определенному пользователю.",
)
async def send_user_message(
    telegram_id: int,
    message: TelegramMessageRequest,
) -> str:
    notifications_services = TelegramNotification(create_bot())
    return await notifications_services.send_user_message(telegram_id, dict(message).get("message"))
