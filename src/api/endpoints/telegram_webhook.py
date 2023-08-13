from fastapi import APIRouter, Request
from telegram import Update

from src.core.exceptions.exceptions import UnauthorizedError
from src.settings import settings

telegram_webhook_router = APIRouter()


if settings.BOT_WEBHOOK_MODE:
    @telegram_webhook_router.post(
        "/webhook",
        description="Получить обновления telegram.",
    )
    async def get_telegram_bot_updates(request: Request) -> dict:
        """Получение обновлений telegram в режиме работы бота webhook."""
        secret_token = request.headers.get("x-telegram-bot-api-secret-token")
        if secret_token != settings.SECRET_KEY:
            raise UnauthorizedError
        bot_instance = request.app.state.bot_instance
        request_json_data = await request.json()
        await bot_instance.update_queue.put(Update.de_json(data=request_json_data, bot=bot_instance.bot))
        return request_json_data
