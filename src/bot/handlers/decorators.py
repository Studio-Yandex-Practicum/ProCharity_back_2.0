from functools import wraps

from dependency_injector.wiring import Provide, inject
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.bot.keyboards import get_unregistered_user_keyboard
from src.bot.services import ExternalSiteUserService
from src.core.depends import Container


def registered_user_required(handler):
    @wraps(handler)
    @inject
    async def decorated_handler(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE,
        ext_site_user_service: ExternalSiteUserService = Provide[
            Container.bot_services_container.bot_site_user_service
        ],
        *args,
        **kwargs
    ):
        telegram_user = update.effective_user
        id_hash = context.args[0] if context.args and len(context.args) == 1 else None
        ext_site_user = (
            await ext_site_user_service.get_by_id_hash(id_hash)
            if id_hash
            else await ext_site_user_service.get_by_telegram_id(telegram_user.id)
        )
        if ext_site_user:
            await handler(update, context, ext_site_user, *args, **kwargs)
        else:
            keyboard = await get_unregistered_user_keyboard()
            await context.bot.send_message(
                chat_id=telegram_user.id,
                text=(
                    "<b>Добро пожаловать на ProCharity!</b>\n\n"
                    "Чтобы получить доступ к боту, "
                    "авторизуйтесь или зарегистрируйтесь на платформе."
                ),
                parse_mode=ParseMode.HTML,
                reply_markup=keyboard,
            )

    return decorated_handler
