from dependency_injector.wiring import Provide
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.bot.constants import callback_data, patterns
from src.bot.keyboards import get_categories_keyboard, get_open_tasks_and_menu_keyboard, get_subcategories_keyboard
from src.bot.services.category import CategoryService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message
from src.core.logging.utils import logger_decor
from src.depends import Container


@logger_decor
@delete_previous_message
async def categories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    category_service: CategoryService = Provide[Container.category_service],
):
    category_service = category_service
    context.user_data["parent_id"] = None
    categories = await category_service.get_unarchived_parents()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_categories_keyboard(categories),
    )


async def confirm_categories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.user_service],
):
    """Записывает выбранные категории в базу данных и отправляет пользователю отчет о выбранных категориях."""
    query = update.callback_query
    telegram_id = update.effective_user.id
    user_service = user_service

    categories = await user_service.get_user_categories(telegram_id)
    if not categories:
        await query.message.edit_text(
            text="Категории не выбраны.",
            reply_markup=await get_open_tasks_and_menu_keyboard(),
        )
    else:
        await query.message.edit_text(
            text="Отлично! Теперь я буду присылать тебе уведомления о новых "
            f"заданиях в категориях: *{', '.join(categories.values())}*.\n\n",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=await get_open_tasks_and_menu_keyboard(),
        )
        await user_service.check_and_set_has_mailing_atribute(telegram_id)


@logger_decor
async def subcategories_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    category_service: CategoryService = Provide[Container.category_service],
    user_service: UserService = Provide[Container.user_service],
):
    query = update.callback_query
    category_service = category_service
    user_service = user_service
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
    category_service: CategoryService = Provide[Container.category_service],
    user_service: UserService = Provide[Container.user_service],
):
    query = update.callback_query
    category_service = category_service
    user_service = user_service
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
    category_service: CategoryService = Provide[Container.category_service],
):
    query = update.callback_query
    category_service = category_service
    categories = await category_service.get_unarchived_parents()

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_categories_keyboard(categories),
    )


def registration_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(subcategories_callback, pattern=patterns.SUBCATEGORIES))
    app.add_handler(CallbackQueryHandler(select_subcategory_callback, pattern=patterns.SELECT_CATEGORY))
    app.add_handler(CallbackQueryHandler(back_subcategory_callback, pattern=patterns.BACK_SUBCATEGORY))
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.CHANGE_CATEGORY))
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.GET_CATEGORIES))
    app.add_handler(CallbackQueryHandler(confirm_categories_callback, pattern=callback_data.CONFIRM_CATEGORIES))
