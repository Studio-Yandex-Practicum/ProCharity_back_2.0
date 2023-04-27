from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes


# ABOUT_PROECT = (f"C ProCharity профессионалы могут помочь некоммерческим"
#     f" организациям в вопросах, которые требуют специальных знаний и опыта."
#     f"\n Интеллектуальный волонтер безвозмездно дарит фонду свое время и"
#     f" профессиональные навыки, позволяя решиать задачи, которые трудно"
#     f" закрыть  силами штатных сотрудников."
# )

async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Это бот платформы интеллектуального волонтерства " "ProCharity",
    )


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create button menu."""
    keyboard = [
        [InlineKeyboardButton("Посмотреть открытые задания", callback_data="1")],
        [InlineKeyboardButton("Изменить компетенции", callback_data="2")],
        [InlineKeyboardButton("Отправить предложение/ошибку", callback_data="3")],
        [InlineKeyboardButton("Задать свой вопрос", callback_data="4")],
        [InlineKeyboardButton("О платформе", callback_data="ABOUT_PROECT")],
        [InlineKeyboardButton(
            " ⏹️ Остановить / ▶️ включить подписку на задания", callback_data="3"
        )],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Please choose:", reply_markup=reply_markup
    )


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    await query.edit_message_text(text=f"Selected option: {query.data}")