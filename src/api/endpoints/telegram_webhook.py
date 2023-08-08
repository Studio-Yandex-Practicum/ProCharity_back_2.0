import json

from fastapi import APIRouter, Request, Depends

from telegram import Update
from src.settings import settings

telegram_webhook_router = APIRouter()

#if settings.BOT_WEBHOOK_MODE:  # TODO Добавить условие!
@telegram_webhook_router.post(
    "/webhook",
    description="Получить обновления telegram.",
    response_description="Обновления получены",
)
async def get_telegram_bot_updates(request: Request):
    """Получение обновлений telegram в режиме работы бота webhook."""
    # if secret_token != settings.SECRET_KEY:  # TODO Добавить проверку!
    #     raise ValueError('UnauthorizedError')

    bot_instance = request.app.state.bot_instance
    #request_json_data = await request.json()  # jsondecodeerror: expecting value: line 1 column 1 (char 0)

    request_scope_dict = request.scope  # Принтом можно вывести словарь, но в json его не получилось перевести
    request_json_data = json.dumps(request_scope_dict)  # TypeError: Object of type bytes is not JSON serializable

    # await bot_instance.update_queue.put(Update.de_json(data=request_json_data, bot=bot_instance.bot))
    # return request_json_data
