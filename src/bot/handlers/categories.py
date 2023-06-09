from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, ContextTypes

from src.bot.constants import callback_data
from src.bot.keyboards import get_categories_keyboard
from src.core.logging.utils import logger_decor
from src.core.services.user import UserService


@logger_decor
async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_service = UserService()
    categories = await user_service.get_user_categories(update.effective_user.id)
    context.user_data["selected_categories"] = {category: None for category in categories}
    context.user_data["parent_id"] = None
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_categories_keyboard(),
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
        await query.message.edit_text(text="Категории не выбраны.")
    else:
        await query.message.edit_text(
            text="Отлично! Теперь я буду присылать тебе уведомления о новых "
            f"заданиях в категориях: *{', '.join(categories.values())}*.\n\n",
            parse_mode=ParseMode.MARKDOWN,
        )
        await user_service.check_and_set_has_mailing_atribute(telegram_id)


def init_app(app: Application):
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.CHANGE_CATEGORY))
    app.add_handler(CallbackQueryHandler(categories_callback, pattern=callback_data.GET_CATEGORIES))
    app.add_handler(CallbackQueryHandler(confirm_categories_callback, pattern=callback_data.CONFIRM_CATEGORIES))
