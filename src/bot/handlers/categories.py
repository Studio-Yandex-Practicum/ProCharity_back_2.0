from dependency_injector.wiring import Provide
from telegram import InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.bot.constants import callback_data, patterns
from src.bot.keyboards import (
    get_checked_categories_keyboard,
    get_subcategories_keyboard,
    get_tasks_and_open_menu_keyboard,
    get_view_categories_keyboard,
)
from src.bot.services.category import CategoryService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message, get_marked_list, registered_user_required
from src.core.db.models import ExternalSiteUser
from src.core.depends import Container
from src.core.logging.utils import logger_decor
from src.core.services.procharity_api import ProcharityAPI

text_chose_category = (
    "Чтобы мне было понятнее, с какими задачами ты готов помогать фондам, "
    "отметь свои профессиональные компетенции (можно выбрать несколько). "
    'После этого нажми "Готово 👌"'
)


@logger_decor
@registered_user_required
@delete_previous_message
async def categories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    category_service: CategoryService = Provide[Container.bot_services_container.bot_category_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    context.user_data["parent_id"] = None
    categories = await category_service.get_unarchived_parents_with_children_count()
    selected_categories_with_parents = await user_service.get_user_categories_with_parents(update.effective_user.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=text_chose_category,
        reply_markup=await get_checked_categories_keyboard(categories, selected_categories_with_parents),
    )


async def view_categories(
    update: Update,
    reply_markup: InlineKeyboardMarkup,
    text_format: str,
    set_has_mailing_attribute: bool = False,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    procharity_api: ProcharityAPI = Provide[Container.core_services_container.procharity_api],
):
    """Выводит список выбранных волонтером категорий в заданном формате и заданную клавиатуру.
    Если set_has_mailing_attribute=True и имеются выбранные категории, выполняется обновление флага подписки.
    """
    query = update.callback_query
    telegram_id = update.effective_user.id
    categories = await user_service.get_user_categories(telegram_id)
    if not categories:
        await query.message.edit_text(
            text="Категории не выбраны.",
            reply_markup=reply_markup,
        )
    else:
        await query.message.edit_text(
            text=text_format.format(categories=get_marked_list(categories.values(), "🎓 ")),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup,
        )
        if set_has_mailing_attribute:
            user = await user_service.get_by_telegram_id(telegram_id)
            has_mailing_changed = await user_service.check_and_set_has_mailing_atribute(user)
            if has_mailing_changed:
                await procharity_api.send_user_bot_status(user)


@logger_decor
@registered_user_required
async def view_current_categories_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, ext_site_user: ExternalSiteUser
):
    """Выводит список выбранных волонтером категорий перед их изменением."""
    text_format = "*Твои профессиональные компетенции:*\n\n" "{categories}\n\n"
    await view_categories(
        update,
        reply_markup=await get_view_categories_keyboard(),
        text_format=text_format,
    )


@logger_decor
@registered_user_required
async def confirm_categories_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE, ext_site_user: ExternalSiteUser
):
    """Выводит список выбранных волонтером категорий после их изменения и включает рассылку (если еще не включена)."""
    text_format = (
        "*Отлично!*\n\n"
        "Теперь сюда будут приходить уведомления о новых заданиях "
        "в следующих категориях:\n\n{categories}\n\n"
        "А пока можешь посмотреть актуальные задания."
    )
    await view_categories(
        update,
        reply_markup=await get_tasks_and_open_menu_keyboard(),
        text_format=text_format,
        set_has_mailing_attribute=True,
    )


@logger_decor
@registered_user_required
async def subcategories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    parent_id = int(context.match.group(1))
    context.user_data["parent_id"] = parent_id
    selected_categories = await user_service.get_user_categories(update.effective_user.id)
    await _display_chose_subcategories_message(update, parent_id, selected_categories)


@logger_decor
@registered_user_required
async def select_subcategory_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    procharity_api: ProcharityAPI = Provide[Container.core_services_container.procharity_api],
):
    subcategory_id = int(context.match.group(1))
    selected_categories = await user_service.get_user_categories(update.effective_user.id)

    if subcategory_id not in selected_categories:
        selected_categories[subcategory_id] = None
        await user_service.add_category_to_user(update.effective_user.id, subcategory_id)
    else:
        del selected_categories[subcategory_id]
        await user_service.delete_category_from_user(update.effective_user.id, subcategory_id)

    user = await user_service.get_by_telegram_id(update.effective_user.id)
    if user and user.external_user:
        await procharity_api.send_user_categories(user.external_user.external_id, selected_categories.keys())

    parent_id = context.user_data["parent_id"]
    await _display_chose_subcategories_message(update, parent_id, selected_categories)


async def _display_chose_subcategories_message(
    update: Update,
    parent_id: int,
    selected_categories: dict[int, str],
    category_service: CategoryService = Provide[Container.bot_services_container.bot_category_service],
) -> None:
    """Отображает сообщение с предложением выбрать подкатегории и кнопки подкатегорий."""
    query = update.callback_query
    parent = await category_service.get(parent_id, is_archived=None)
    subcategories = await category_service.get_unarchived_subcategories(parent_id)
    await query.message.edit_text(
        f'Ты выбрал категорию <b>"{parent.name}"</b>. Отметь любое количество компетенций и нажми "Назад ⬅️"',
        reply_markup=await get_subcategories_keyboard(parent_id, subcategories, selected_categories),
        parse_mode=ParseMode.HTML,
    )


@logger_decor
@registered_user_required
async def back_subcategory_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
    category_service: CategoryService = Provide[Container.bot_services_container.bot_category_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    query = update.callback_query
    categories = await category_service.get_unarchived_parents_with_children_count()
    selected_categories_with_parents = await user_service.get_user_categories_with_parents(update.effective_user.id)

    await query.message.edit_text(
        text_chose_category,
        reply_markup=await get_checked_categories_keyboard(categories, selected_categories_with_parents),
    )


def registration_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(subcategories_callback, pattern=patterns.SUBCATEGORIES))
    app.add_handler(CallbackQueryHandler(select_subcategory_callback, pattern=patterns.SELECT_CATEGORY))
    app.add_handler(CallbackQueryHandler(back_subcategory_callback, pattern=patterns.BACK_SUBCATEGORY))
    app.add_handler(CallbackQueryHandler(view_current_categories_callback, pattern=callback_data.VIEW_CATEGORIES))
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.CHANGE_CATEGORY))
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.GET_CATEGORIES))
    app.add_handler(CallbackQueryHandler(confirm_categories_callback, pattern=callback_data.CONFIRM_CATEGORIES))
