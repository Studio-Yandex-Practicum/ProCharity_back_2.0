from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import Application, CommandHandler, ContextTypes

from src.bot.constants import callback_data, commands
from src.core.logging.utils import logger_decor
from src.core.services.user import UserService


@logger_decor
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_service = UserService()
    await user_service.register_user(
        telegram_id=update.effective_chat.id,
        username=update.effective_chat.username,
    )
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="Начнём",
                    callback_data=callback_data.CHANGE_CATEGORY,
                )
            ]
        ]
    )

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


def init_app(app: Application):
    app.add_handler(CommandHandler(commands.START, start_command))
