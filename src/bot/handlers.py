from telegram import Update, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.buttons import MENU_KEYBOARD


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Это бот платформы интеллектуального волонтерства " "ProCharity",
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create button menu."""
    keyboard = MENU_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выбери, что тебя интересует:", reply_markup=reply_markup
    )


async def send_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # TODO delete this
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")
