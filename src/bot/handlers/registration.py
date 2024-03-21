from typing import Never

from dependency_injector.wiring import Provide, inject
from telegram import Update
from telegram.ext import Application, ChatMemberHandler, CommandHandler, ContextTypes

from src.bot.constants import commands
from src.bot.keyboards import get_start_keyboard, get_unregistered_user_keyboard
from src.bot.services import ExternalSiteUserService, UserService
from src.core.depends import Container
from src.core.logging.utils import logger_decor


@logger_decor
@inject
async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    ext_site_user_service: ExternalSiteUserService = Provide[Container.bot_services_container.bot_site_user_service],
):
    telegram_user = update.effective_user
    id_hash = context.args[0] if len(context.args) == 1 else None
    ext_site_user = (
        await ext_site_user_service.get_by_id_hash(id_hash)
        if id_hash
        else await ext_site_user_service.get_by_telegram_id(telegram_user.id)
    )

    if ext_site_user:
        await user_service.register_or_update_user(ext_site_user, telegram_user)
        keyboard = await get_start_keyboard()
        await context.bot.send_message(
            chat_id=telegram_user.id,
            text="Авторизация прошла успешно!\n\n"
            "Теперь оповещения будут приходить сюда. "
            "Изменить настройку уведомлений можно в личном кабинете.\n\n",
            reply_markup=keyboard,
        )

    else:
        keyboard = await get_unregistered_user_keyboard()
        await context.bot.send_message(
            chat_id=telegram_user.id,
            text=(
                "<b>Добро пожаловать на ProCharity!</b>\n\n"
                "Чтобы получить доступ к боту, "
                "авторизуйтесь или зарегистрируйтесь на платформе."
            ),
            parse_mode="HTML",
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
