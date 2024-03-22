from typing import Never

from dependency_injector.wiring import Provide, inject
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes

from src.bot.constants import commands
from src.bot.keyboards import get_start_keyboard
from src.bot.services import UserService
from src.core.db.models import ExternalSiteUser
from src.core.depends import Container
from src.core.logging.utils import logger_decor

from .decorators import registered_user_required


@logger_decor
@registered_user_required
@inject
async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    telegram_user = update.effective_user
    await user_service.register_or_update_user(ext_site_user, telegram_user)
    keyboard = await get_start_keyboard()
    await context.bot.send_message(
        chat_id=telegram_user.id,
        text="Авторизация прошла успешно!\n\n"
        "Теперь оповещения будут приходить сюда. "
        "Изменить настройку уведомлений можно в личном кабинете.\n\n",
        reply_markup=keyboard,
    )


@logger_decor
@inject
async def on_chat_member_update(
    update: Update,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    my_chat_member = update.my_chat_member or Never
    effective_user = update.effective_user or Never
    user = await user_service.get_by_telegram_id(effective_user.id)

    if user is None:
        return None

    if (
        my_chat_member.new_chat_member.status == my_chat_member.new_chat_member.BANNED
        and my_chat_member.old_chat_member.status == my_chat_member.old_chat_member.MEMBER
    ):
        return await user_service.bot_banned(user)
    if (
        my_chat_member.new_chat_member.status == my_chat_member.new_chat_member.MEMBER
        and my_chat_member.old_chat_member.status == my_chat_member.old_chat_member.BANNED
    ):
        return await user_service.bot_unbanned(user)

    return None


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.START, start_command))
    app.add_handler(ChatMemberHandler(on_chat_member_update, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER))
