from dependency_injector.wiring import Provide
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.bot.constants import callback_data, patterns
from src.bot.keyboards import (
    get_checked_categories_keyboard,
    get_open_tasks_and_menu_keyboard,
    get_subcategories_keyboard,
    get_view_categories_keyboard,
)
from src.bot.services.category import CategoryService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message, get_marked_list
from src.core.depends import Container
from src.core.logging.utils import logger_decor


@logger_decor
@delete_previous_message
async def categories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    category_service: CategoryService = Provide[Container.bot_services_container.bot_category_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    context.user_data["parent_id"] = None
    categories = await category_service.get_unarchived_parents_with_children_count()
    selected_categories_with_parents = await user_service.get_user_categories_with_parents(update.effective_user.id)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_checked_categories_keyboard(categories, selected_categories_with_parents),
    )


async def view_categories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    """Выводит список выбранных волонтером категорий."""
    query = update.callback_query
    telegram_id = update.effective_user.id

    categories = await user_service.get_user_categories(telegram_id)
    if not categories:
        await query.message.edit_text(
            text="Категории не выбраны.",
            reply_markup=await get_view_categories_keyboard(),
        )
    else:
        await query.message.edit_text(
            text=(
                "*Твои профессиональные компетенции:*\n\n" "{}\n\n".format(get_marked_list(categories.values(), "🎓 "))
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await get_view_categories_keyboard(),
        )


async def confirm_categories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    """Записывает выбранные категории в базу данных и отправляет пользователю отчет о выбранных категориях."""
    query = update.callback_query
    telegram_id = update.effective_user.id

    categories = await user_service.get_user_categories(telegram_id)
    if not categories:
        await query.message.edit_text(
            text="Категории не выбраны.",
            reply_markup=await get_open_tasks_and_menu_keyboard(),
        )
    else:
        await query.message.edit_text(
            text=(
                "*Отлично!*\n\n"
                "Теперь сюда будут приходить уведомления о новых заданиях "
                "в следующих категориях:\n\n{}\n\n"
                "А пока можешь посмотреть актуальные задания.".format(get_marked_list(categories.values(), "🎓 "))
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await get_open_tasks_and_menu_keyboard(),
        )
        await user_service.check_and_set_has_mailing_atribute(telegram_id)


async def all_right_categories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    """Записывает выбранные категории в базу данных и отправляет пользователю отчет о выбранных категориях."""
    query = update.callback_query
    telegram_id = update.effective_user.id

    categories = await user_service.get_user_categories(telegram_id)
    if not categories:
        await query.message.edit_text(
            text="Категории не выбраны.",
            reply_markup=await get_open_tasks_and_menu_keyboard(),
        )
    else:
        await query.message.edit_text(
            text=(
                "*Отлично!*\n\n"
                "Теперь сюда будут приходить уведомления о новых заданиях "
                "в следующих категориях:\n\n{}\n\n"
                "А пока можешь посмотреть актуальные задания.".format(get_marked_list(categories.values(), "🎓 "))
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await get_open_tasks_and_menu_keyboard(),
        )
        # стоит ли опять проверять mailing если мы ничего не меняли?
        # await user_service.check_and_set_has_mailing_atribute(telegram_id)


@logger_decor
async def subcategories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    category_service: CategoryService = Provide[Container.bot_services_container.bot_category_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    query = update.callback_query
    parent_id = int(context.match.group(1))
    context.user_data["parent_id"] = parent_id
    subcategories = await category_service.get_unarchived_subcategories(parent_id)
    selected_categories = await user_service.get_user_categories(update.effective_user.id)

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, subcategories, selected_categories),
    )


@logger_decor
async def select_subcategory_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    category_service: CategoryService = Provide[Container.bot_services_container.bot_category_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    query = update.callback_query
    subcategory_id = int(context.match.group(1))
    selected_categories = await user_service.get_user_categories(update.effective_user.id)

    if subcategory_id not in selected_categories:
        selected_categories[subcategory_id] = None
        await user_service.add_category_to_user(update.effective_user.id, subcategory_id)
    else:
        del selected_categories[subcategory_id]
        await user_service.delete_category_from_user(update.effective_user.id, subcategory_id)

    parent_id = context.user_data["parent_id"]
    subcategories = await category_service.get_unarchived_subcategories(parent_id)

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, subcategories, selected_categories),
    )


@logger_decor
async def back_subcategory_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    category_service: CategoryService = Provide[Container.bot_services_container.bot_category_service],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    query = update.callback_query
    categories = await category_service.get_unarchived_parents_with_children_count()
    selected_categories_with_parents = await user_service.get_user_categories_with_parents(update.effective_user.id)

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_checked_categories_keyboard(categories, selected_categories_with_parents),
    )


def registration_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(subcategories_callback, pattern=patterns.SUBCATEGORIES))
    app.add_handler(CallbackQueryHandler(select_subcategory_callback, pattern=patterns.SELECT_CATEGORY))
    app.add_handler(CallbackQueryHandler(back_subcategory_callback, pattern=patterns.BACK_SUBCATEGORY))
    app.add_handler(CallbackQueryHandler(view_categories_callback, pattern=callback_data.VIEW_CATEGORIES))
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.CHANGE_CATEGORY))
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.GET_CATEGORIES))
    app.add_handler(CallbackQueryHandler(confirm_categories_callback, pattern=callback_data.CONFIRM_CATEGORIES))
    app.add_handler(CallbackQueryHandler(all_right_categories_callback, pattern=callback_data.ALL_RIGHT_CATEGORIES))
