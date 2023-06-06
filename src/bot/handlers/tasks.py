from telegram import Update
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.bot.constants import patterns
from src.bot.keyboards import get_categories_keyboard, get_subcategories_keyboard
from src.core.logging.utils import logger_decor


def init_app(app: Application):
    app.add_handler(CallbackQueryHandler(subcategories_callback, pattern=patterns.SUBCATEGORIES))
    app.add_handler(CallbackQueryHandler(select_subcategory_callback, pattern=patterns.SELECT_CATEGORY))
    app.add_handler(CallbackQueryHandler(back_subcategory_callback, pattern=patterns.BACK_SUBCATEGORY))


@logger_decor
async def subcategories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parent_id = int(context.match.group(1))
    context.user_data["parent_id"] = parent_id

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, context),
    )


@logger_decor
async def select_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    subcategory_id = int(context.match.group(1))
    selected_categories = context.user_data.setdefault("selected_categories", {})

    if subcategory_id not in selected_categories:
        selected_categories[subcategory_id] = None
    else:
        del selected_categories[subcategory_id]

    parent_id = context.user_data["parent_id"]

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, context),
    )


@logger_decor
async def back_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_categories_keyboard(),
    )
