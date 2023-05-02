from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes

from src.bot import constants as bot_constants
from src.core.services.user import UserService


async def start_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    user_service = UserService()
    await user_service.register_user(
        telegram_id=update.effective_chat.id,
        username=update.effective_chat.username,
    )
    callback_data = bot_constants.COMMAND__GREETING
    button = [[InlineKeyboardButton(text="Начнём", callback_data=callback_data)]]
    keyboard = InlineKeyboardMarkup(button)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! 👋 \n\n"
        'Я бот платформы интеллектуального волонтерства <a href="https://procharity.ru/">ProCharity</a>. '
        "Буду держать тебя в курсе новых задач и помогу "
        "оперативно связаться с командой поддержки.",
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )
    return bot_constants.GREETING
