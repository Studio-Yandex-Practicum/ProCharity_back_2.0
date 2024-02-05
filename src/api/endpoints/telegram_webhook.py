from fastapi import APIRouter, Request
from telegram import Update

from src.core.exceptions.exceptions import UnauthorizedError, WebhookOnError
from src.settings import settings

telegram_webhook_router = APIRouter(redirect_slashes=False)


@telegram_webhook_router.post(path="/webhook/", include_in_schema=False)
@telegram_webhook_router.post(
    path="/webhook",
    description="Получить обновления telegram.",
)
async def get_telegram_bot_updates(request: Request) -> None:
    """Получение обновлений telegram в режиме работы бота webhook."""
    if not settings.BOT_WEBHOOK_MODE:
        raise WebhookOnError
    telegram_secret_token = request.headers.get("x-telegram-bot-api-secret-token")
    if telegram_secret_token != settings.TELEGRAM_SECRET_TOKEN:
        raise UnauthorizedError
    bot_instance = request.app.state.bot_instance
    request_json_data = await request.json()
    await bot_instance.update_queue.put(Update.de_json(data=request_json_data, bot=bot_instance.bot))
