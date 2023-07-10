from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from src.bot.constants import callback_data, commands
from src.bot.keyboards import get_confirm_keyboard, get_start_keyboard
from src.bot.services.user import UserService
from src.core.logging.utils import logger_decor


@logger_decor
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_service = UserService()
    await user_service.register_user(
        telegram_id=update.effective_user.id,
        username=update.effective_chat.username,
        first_name=update.effective_chat.first_name,
        last_name=update.effective_chat.last_name,
    )
    categories = await user_service.get_user_categories(update.effective_user.id)
    callback_data_on_start = commands.GREETING_REGISTERED_USER if categories else callback_data.CHANGE_CATEGORY
    keyboard = await get_start_keyboard(callback_data_on_start=callback_data_on_start)

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="Привет! 👋 \n\n"
        'Я бот платформы интеллектуального волонтерства <a href="https://procharity.ru/">ProCharity</a>. '
        "Буду держать тебя в курсе новых задач и помогу "
        "оперативно связаться с командой поддержки.\n\n",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@logger_decor
async def confirm_chosen_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = get_confirm_keyboard()

    user_service = UserService()
    categories = await user_service.get_user_categories(update.effective_user.id)
    text = ", ".join(categories.values())

    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=f"Вот список твоих профессиональных компетенций: *{text}* Все верно?",
        reply_markup=keyboard,
        parse_mode=ParseMode.MARKDOWN,
    )


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.START, start_command))
    app.add_handler(CallbackQueryHandler(confirm_chosen_categories, pattern=commands.GREETING_REGISTERED_USER))
