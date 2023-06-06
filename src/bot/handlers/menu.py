import json
import urllib

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.ext import Application, CallbackContext, CallbackQueryHandler, CommandHandler, MessageHandler
from telegram.ext.filters import StatusUpdate

from src.api.schemas import FeedbackFormQueryParams
from src.bot.constants import callback_data, commands
from src.bot.keyboards import MENU_KEYBOARD
from src.core.logging.utils import logger_decor
from src.settings import settings


def init_app(app: Application):
    app.add_handler(CommandHandler(commands.MENU, menu_callback))
    app.add_handler(CallbackQueryHandler(ask_your_question, pattern=callback_data.ASK_YOUR_QUESTION))
    app.add_handler(CallbackQueryHandler(ask_your_question, pattern=callback_data.SEND_ERROR_OR_PROPOSAL))
    app.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data))


@logger_decor
async def menu_callback(update: Update, context: CallbackContext):
    """Create button menu."""
    keyboard = MENU_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери, что тебя интересует:", reply_markup=reply_markup)


@logger_decor
async def ask_your_question(update: Update, context: CallbackContext):
    text = "Задать вопрос"
    name = update.effective_user["first_name"]
    surname = update.effective_user["last_name"]
    query_params = FeedbackFormQueryParams(name=name, surname=surname)
    if update.effective_message.web_app_data:
        text = "Исправить неверно внесенные данные"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Нажмите на кнопку ниже, чтобы задать вопрос.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=text,
                web_app=WebAppInfo(
                    url=urllib.parse.urljoin(settings.feedback_form_template_url, query_params.as_url_query())
                ),
            )
        ),
    )


@logger_decor
async def web_app_data(update: Update):
    user_data = json.loads(update.effective_message.web_app_data.data)
    buttons = [
        [InlineKeyboardButton(text="Открыть в меню", callback_data=callback_data.MENU)],
        [InlineKeyboardButton(text="Посмотреть открытые задания", callback_data=callback_data.VIEW_TASKS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        text=f"Спасибо, я передал информацию команде ProCharity! Ответ придет на почту {user_data['email']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        text="Вы можете вернуться в меню или посмотреть открытые задания. Нажмите на нужную кнопку.",
        reply_markup=keyboard,
    )
