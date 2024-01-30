from dependency_injector.wiring import Provide, inject
from telegram import ChatMember, ChatMemberUpdated, Update
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
    ext_user = await ext_user_service.get_ext_user_by_args(context.args)
    if ext_user is not None:
        await user_service.register_user(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=ext_user.first_name,
            last_name=ext_user.last_name,
            email=ext_user.email,
            external_id=ext_user.id,
        )
        await user_service.set_categories_to_user(update.effective_user.id, ext_user.specializations)
        url_connect = get_connection_url(update.effective_user.id, ext_user.id)
    else:
        await user_service.register_user(
            telegram_id=update.effective_user.id,
            username=update.effective_user.username,
            first_name=update.effective_user.first_name,
            last_name=update.effective_user.last_name,
        )
        url_connect = get_connection_url(update.effective_user.id)
    categories = await user_service.get_user_categories(update.effective_user.id)
    callback_data_on_start = commands.GREETING_REGISTERED_USER if categories else callback_data.CHANGE_CATEGORY
    keyboard = await get_start_keyboard(callback_data_on_start=callback_data_on_start, url_for_connection=url_connect)
    keyboard_feedback = await feedback_buttons(update.effective_user)
    await context.bot.send_message(
        chat_id=update.effective_user.id,
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


def extract_status_change(chat_member_update: ChatMemberUpdated):
    status_change = chat_member_update.difference().get("status")
    old_is_member, new_is_member = chat_member_update.difference().get("is_member", (None, None))

    if status_change is None:
        return None

    old_status, new_status = status_change
    was_member = old_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (old_status == ChatMember.BANNED and old_is_member is True)
    is_member = new_status in [
        ChatMember.MEMBER,
        ChatMember.OWNER,
        ChatMember.ADMINISTRATOR,
    ] or (new_status == ChatMember.BANNED and new_is_member is True)

    return was_member, is_member


@logger_decor
@inject
async def on_chat_member_update(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_user_service: ExternalSiteUserService = Provide[Container.bot_services_container.bot_site_user_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    result = extract_status_change(update.effective_user.id)

    if result is None:
        return

    old_status, new_status = result
    if old_status == ChatMember.MEMBER and new_status == ChatMember.BANNED:
        await user_service.user_banned(telegram_id=update.effective_user.id)
    elif old_status == ChatMember.BANNED and new_status == ChatMember.MEMBER:
        await user_service.user_unbanned(telegram_id=update.effective_user.id)


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.START, start_command))
    app.add_handler(CallbackQueryHandler(confirm_chosen_categories, pattern=commands.GREETING_REGISTERED_USER))
    app.add_handler(ChatMemberHandler(on_chat_member_update, chat_member_types=ChatMemberHandler.MY_CHAT_MEMBER))
