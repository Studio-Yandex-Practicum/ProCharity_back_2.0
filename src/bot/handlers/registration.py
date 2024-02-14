from dependency_injector.wiring import Provide, inject
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, ChatMemberHandler, CommandHandler, ContextTypes

from src.bot.constants import callback_data, commands
from src.bot.keyboards import feedback_buttons, get_confirm_keyboard, get_start_keyboard
from src.bot.services.external_site_user import ExternalSiteUserService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message, get_connection_url
from src.core.depends import Container
from src.core.logging.utils import logger_decor
from src.settings import Settings


@logger_decor
@inject
async def start_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_user_service: ExternalSiteUserService = Provide[Container.bot_services_container.bot_site_user_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    settings: Settings = Provide[Container.settings],
):
    telegram_user = update.effective_user
    ext_user, created = await ext_user_service.get_or_create(id_hash=context.args[0] if context.args else None)
    if created or ext_user is None:
        user = await user_service.register_user(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name,
        )
        url_connect = get_connection_url(telegram_user.id)
    elif ext_user is not None:
        user = await user_service.register_user(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=ext_user.first_name,
            last_name=ext_user.last_name,
            email=ext_user.email,
            external_id=ext_user.external_id,
        )
        await user_service.set_categories_to_user(telegram_user.id, ext_user.specializations)
        url_connect = get_connection_url(telegram_user.id, ext_user.id)
    categories = await user_service.get_user_categories(telegram_user.id)
    callback_data_on_start = commands.GREETING_REGISTERED_USER if categories else callback_data.CHANGE_CATEGORY
    keyboard = await get_start_keyboard(callback_data_on_start=callback_data_on_start, url_for_connection=url_connect)
    keyboard_feedback = await feedback_buttons(user)
    await context.bot.send_message(
        chat_id=telegram_user.id,
        text="Привет! 👋 \n\n",
        reply_markup=keyboard_feedback,
    )
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f'Я бот платформы интеллектуального волонтерства <a href="{settings.PROCHARITY_URL}">ProCharity</a>. '
        "Буду держать тебя в курсе новых задач и помогу "
        "оперативно связаться с командой поддержки.\n\n",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@logger_decor
@delete_previous_message
async def confirm_chosen_categories(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    keyboard = get_confirm_keyboard()
    categories = await user_service.get_user_categories(update.effective_user.id)
    context.user_data["selected_categories"] = {category: None for category in categories}
    text = ", ".join(categories.values())

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Вот список твоих профессиональных компетенций: *{text}* Все верно?",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


@logger_decor
@inject
async def on_chat_member_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_user_service: ExternalSiteUserService = Provide[Container.bot_services_container.bot_site_user_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    user = await user_service.get_by_telegram_id(update.effective_user.id)

    if user is None:
        return None

    if (
        update.my_chat_member.new_chat_member.status == update.my_chat_member.new_chat_member.BANNED
        and update.my_chat_member.old_chat_member.status == update.my_chat_member.old_chat_member.MEMBER
    ):
        return await user_service.bot_banned(user)
    if (
        update.my_chat_member.new_chat_member.status == update.my_chat_member.new_chat_member.MEMBER
        and update.my_chat_member.old_chat_member.status == update.my_chat_member.old_chat_member.BANNED
    ):
        return await user_service.bot_unbanned(user)

    return None


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.START, start_command))
    app.add_handler(CallbackQueryHandler(confirm_chosen_categories, pattern=commands.GREETING_REGISTERED_USER))
    app.add_handler(ChatMemberHandler(on_chat_member_update, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER))
