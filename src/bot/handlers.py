from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from constaints.callback_data import (VIEW, CHANGE, SEND,
                                      ASK, ABOUT, SUBSCRIPTION)
from buttons import (VIEW_OPENED_JOBS, CHANGE_COMPETENCIES,
                     SEND_SUGGESTION_BUG, ASK_QUESTION,
                     ABOUT_PLATFORM, START_STOP_SUBSCRIPTION)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Это бот платформы интеллектуального волонтерства " "ProCharity",
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create button menu."""
    keyboard = [
        [InlineKeyboardButton(
            VIEW_OPENED_JOBS,
            callback_data=VIEW
        )],
        [InlineKeyboardButton(
            CHANGE_COMPETENCIES,
            callback_data=CHANGE
        )],
        [InlineKeyboardButton(
            SEND_SUGGESTION_BUG,
            callback_data=SEND
        )],
        [InlineKeyboardButton(
            ASK_QUESTION,
            callback_data=ASK
        )],
        [InlineKeyboardButton(
            ABOUT_PLATFORM,
            callback_data=ABOUT
        )],
        [InlineKeyboardButton(
            START_STOP_SUBSCRIPTION,
            callback_data=SUBSCRIPTION
        )],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выбери, что тебя интересует:", reply_markup=reply_markup
    )


async def send_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # TODO delete this
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")
