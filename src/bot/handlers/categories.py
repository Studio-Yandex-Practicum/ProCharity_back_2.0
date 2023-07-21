from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.bot.constants import callback_data
from src.bot.keyboards import get_categories_keyboard, get_open_tasks_and_menu_keyboard, get_subcategories_keyboard
from src.bot.services.category import CategoryService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message
from src.core.logging.utils import logger_decor


@logger_decor
@delete_previous_message
async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_service = UserService()
    category_service = CategoryService()
    user_categories = await user_service.get_user_categories(update.effective_user.id)
    context.user_data["selected_categories"] = {category: None for category in user_categories}
    context.user_data["parent_id"] = None
    categories = await category_service.get_unarchived_parents()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Чтобы я знал, с какими задачами ты готов помогать, "
             "выбери свои профессиональные компетенции (можно выбрать "
             'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_categories_keyboard(categories),
    )


async def confirm_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Записывает выбранные категории в базу данных и отправляет пользователю отчет о выбранных категориях."""
    query = update.callback_query
    telegram_id = update.effective_user.id
    user_service = UserService()

    users_categories_ids = context.user_data.get("selected_categories", {}).keys()

    await user_service.set_categories_to_user(
        telegram_id=telegram_id,
        categories_ids=users_categories_ids,
    )

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
async def subcategories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    category_service = CategoryService()
    query = update.callback_query
    parent_id = int(context.match.group(1))
    context.user_data["parent_id"] = parent_id
    subcategories = await category_service.get_unarchived_subcategories(parent_id)
    selected_categories = context.user_data.get("selected_categories", {})

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, subcategories, selected_categories),
    )


@logger_decor
async def select_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category_service = CategoryService()
    subcategory_id = int(context.match.group(1))
    selected_categories = context.user_data.get("selected_categories", {})

    if subcategory_id not in selected_categories:
        selected_categories[subcategory_id] = None
    else:
        del selected_categories[subcategory_id]

    parent_id = context.user_data["parent_id"]
    subcategories = await category_service.get_unarchived_subcategories(parent_id)

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, subcategories, selected_categories),
    )


@logger_decor
async def back_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    category_service = CategoryService()
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
