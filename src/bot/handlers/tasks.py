from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, ContextTypes

from src.bot.constants import callback_data, patterns
from src.bot.keyboards import get_categories_keyboard, get_back_menu, get_subcategories_keyboard
from src.bot.services.category import CategoryService
from src.bot.services.task import TaskService
from src.core.logging.utils import logger_decor
from src.core.utils import display_tasks


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


@logger_decor
async def view_task_callback(update: Update, context: CallbackContext, limit: int = 3):
    task_service = TaskService()
    tasks = await task_service.get_user_tasks(limit)

    for task in tasks:
        message = display_tasks(task)
        await context.bot.send_message(
            chat_id=update.effective_chat.id, text=message, parse_mode=ParseMode.HTML, disable_web_page_preview=True
        )
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="### Здесь текст о наличии заданий, или возврата в меню:\n"
             "Есть ещё задания, показать?:",
        reply_markup=await get_back_menu(),
    )


def registration_handlers(app: Application):
    app.add_handler(CallbackQueryHandler(subcategories_callback, pattern=patterns.SUBCATEGORIES))
    app.add_handler(CallbackQueryHandler(select_subcategory_callback, pattern=patterns.SELECT_CATEGORY))
    app.add_handler(CallbackQueryHandler(back_subcategory_callback, pattern=patterns.BACK_SUBCATEGORY))
    app.add_handler(CallbackQueryHandler(view_task_callback, pattern=callback_data.VIEW_TASKS))
