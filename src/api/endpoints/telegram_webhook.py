from fastapi import APIRouter, Request

from src.settings import settings

# from telegram import Update


telegram_webhook_router = APIRouter()


if settings.BOT_WEBHOOK_MODE:
    print(f"BOT_WEBHOOK_MODE: {settings.BOT_WEBHOOK_MODE}")

    @telegram_webhook_router.post(
        "/webhook",
        description="Получить обновления telegram.",
    )
    async def get_telegram_bot_updates(request: Request):
        """Получение обновлений telegram в режиме работы бота webhook."""
        print(f"request_scope: {request.scope}")  # Печатает словарь
        request_json_data = await request.json()  # -> !!! Падает с JSONDecodeError

        print(f"request_json_data: {request_json_data}")
        # --->>> !!! JSONDecodeError: Expecting value: line 1 column 1 (char 0)
