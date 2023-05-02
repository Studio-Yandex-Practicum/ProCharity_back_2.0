from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Это бот платформы интеллектуального волонтерства " "ProCharity",
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create button menu."""
    keyboard = [
        [InlineKeyboardButton(
            "Посмотреть открытые задания",
            callback_data="view_tasks"
        )],
        [InlineKeyboardButton(
            "Изменить компетенции",
            callback_data="change_category"
        )],
        [InlineKeyboardButton(
            "Отправить предложение/ошибку",
            callback_data="send_error_or_proposal"
        )],
        [InlineKeyboardButton(
            "Задать свой вопрос",
            callback_data="ask_your_question"
        )],
        [InlineKeyboardButton(
            "О платформе",
            callback_data="about_project"
        )],
        [InlineKeyboardButton(
            "⏹️ Остановить / ▶️ включить подписку на задания",
            callback_data="job_subscription"
        )],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Выбери, что тебя интересует:", reply_markup=reply_markup
    )


async def send_callback_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:  # TODO delete this
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")