import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import Application, ContextTypes, MessageHandler
from telegram.ext.filters import StatusUpdate

from src.bot.constants import callback_data
from src.bot.schemas import FeedbackModel
from src.core.logging.utils import logger_decor
from src.core.services.email import EmailProvider
from src.settings import settings


@logger_decor
async def web_app_data_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = json.loads(update.effective_message.web_app_data.data)
    buttons = [
        [InlineKeyboardButton(text="Открыть меню", callback_data=callback_data.MENU)],
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
    email_provider = EmailProvider()
    feedback = FeedbackModel.model_validate(user_data)
    await email_provider.send_question_feedback(
        telegram_id=update.effective_user.id,
        message=feedback.to_message(),
        email=settings.EMAIL_ADMIN,
    )


def registration_handlers(app: Application):
    app.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data_handler))
