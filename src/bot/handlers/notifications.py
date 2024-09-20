from dependency_injector.wiring import Provide, inject
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.api.services.external_site_user import ExternalSiteUserService
from src.bot.constants import callback_data, patterns
from src.bot.keyboards import get_back_menu, get_notification_settings_keyboard
from src.bot.services import UserService
from src.bot.utils import registered_user_required
from src.core.db.models import ExternalSiteUser
from src.core.depends import Container
from src.core.logging.utils import logger_decor
from src.core.services.procharity_api import ProcharityAPI

text_notification_settings_volunteer = 'Выбери, какие уведомления хочешь получать в боте, и нажми кнопку "Готово 👌"'
text_notification_settings_fund = 'Выберите, какие уведомления вы хотите получать в боте, и нажмите кнопку "Готово 👌"'


@logger_decor
@registered_user_required
@inject
async def notification_settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    query = update.callback_query
    telegram_id = update.effective_user.id
    user = await user_service.get_by_telegram_id(telegram_id)
    text = text_notification_settings_volunteer if user.is_volunteer else text_notification_settings_fund
    await query.message.edit_text(
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_notification_settings_keyboard(user),
    )


@logger_decor
@registered_user_required
@inject
async def confirm_notification_settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    volunteer_auth_url: str = Provide[Container.settings.provided.procharity_volunteer_auth_url],
    fund_auth_url: str = Provide[Container.settings.provided.procharity_fund_auth_url],
):
    query = update.callback_query
    telegram_id = update.effective_user.id
    user = await user_service.get_by_telegram_id(telegram_id)
    filling = ("Ты можешь", volunteer_auth_url) if user.is_volunteer else ("Вы можете", fund_auth_url)
    text = (
        "Настройки уведомлений сохранены. {} изменить их в любой момент "
        'в меню бота или в <a href="{}">личном кабинете</a>.'
    ).format(*filling)
    await query.message.edit_text(
        text=text,
        parse_mode=ParseMode.HTML,
        reply_markup=await get_back_menu(),
        disable_web_page_preview=True,
    )


@logger_decor
@registered_user_required
async def notification_field_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    site_user_service: ExternalSiteUserService = Provide[Container.bot_services_container.bot_site_user_service],
    procharity_api: ProcharityAPI = Provide[Container.core_services_container.procharity_api],
):
    query = update.callback_query
    user = await user_service.get_by_telegram_id(update.effective_user.id)
    field = context.match.group(1)
    await site_user_service.toggle_has_mailing(user.external_user.external_id, field)
    await procharity_api.send_user_bot_status(user)
    text = text_notification_settings_volunteer if user.is_volunteer else text_notification_settings_fund
    await query.message.edit_text(
        text=text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_notification_settings_keyboard(user),
    )


def registration_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(notification_settings, pattern=callback_data.NOTIFICATION_SETTINGS))
    app.add_handler(
        CallbackQueryHandler(confirm_notification_settings, pattern=callback_data.CONFIRM_NOTIFICATION_SETTINGS)
    )
    app.add_handler(CallbackQueryHandler(notification_field_callback, pattern=patterns.NOTIFICATION_FIELD_CALLBACK))
