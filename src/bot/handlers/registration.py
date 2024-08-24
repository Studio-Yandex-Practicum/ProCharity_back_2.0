from typing import Never

from dependency_injector.wiring import Provide, inject
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes

from src.bot.constants import commands
from src.bot.keyboards import get_start_keyboard
from src.bot.services import UserService
from src.bot.utils import registered_user_required
from src.core.db.models import ExternalSiteUser
from src.core.depends import Container
from src.core.logging.utils import logger_decor
from src.core.services.procharity_api import ProcharityAPI


@logger_decor
@registered_user_required
@inject
async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    volunteer_auth_url: str = Provide[Container.settings.provided.procharity_volunteer_auth_url],
    fund_auth_url: str = Provide[Container.settings.provided.procharity_fund_auth_url],
):
    telegram_user = update.effective_user or Never
    user = await user_service.register_user(ext_site_user, telegram_user)
    auth_url = volunteer_auth_url if user.is_volunteer else fund_auth_url

    await context.bot.send_message(
        chat_id=telegram_user.id,
        text="<b>Авторизация прошла успешно!</b>\n\n"
        "Теперь оповещения будут приходить сюда. "
        f'Изменить настройку уведомлений можно в <a href="{auth_url}">личном кабинете</a>.\n\n'
        "Навигация по боту запускается командой /menu.",
        parse_mode=ParseMode.HTML,
        reply_markup=await get_start_keyboard(user),
        disable_web_page_preview=True,
    )


@logger_decor
@inject
async def on_chat_member_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    procharity_api: ProcharityAPI = Provide[Container.core_services_container.procharity_api],
):
    """Обновление статуса пользователя."""
    my_chat_member = update.my_chat_member or Never

    if not my_chat_member:
        return None

    effective_user = update.effective_user or Never
    user = await user_service.get_by_telegram_id(effective_user.id)

    if not user:
        return None
    if my_chat_member.new_chat_member.status == my_chat_member.new_chat_member.BANNED:
        await user_service.bot_banned(user)
    elif my_chat_member.new_chat_member.status == my_chat_member.new_chat_member.MEMBER:
        await user_service.bot_unbanned(user)
    await procharity_api.send_user_bot_status(user)
    unblock_text = (
        "<b>Вы разблокировали бот ProCharity</b>\n\n"
        if user.is_volunteer
        else "<b>Ты разблокировал бот ProCharity</b>\n\n"
    )
    await context.bot.send_message(
        chat_id=effective_user.id,
        text=unblock_text,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    return user


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.START, start_command))
    app.add_handler(ChatMemberHandler(on_chat_member_update))
