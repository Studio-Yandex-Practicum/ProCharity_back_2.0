import json
import urllib

import structlog
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
    WebAppInfo,
)
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes, MessageHandler
from telegram.ext.filters import StatusUpdate

from src.api.schemas import FeedbackFormQueryParams
from src.bot.constants import callback_data, commands, enum, patterns
from src.bot.keyboards import get_back_menu, get_menu_keyboard, get_no_mailing_keyboard
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message
from src.core.logging.utils import logger_decor
from src.settings import settings

log = structlog.get_logger()


@logger_decor
@delete_previous_message
async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Возвращает в меню."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери, что тебя интересует:",
        reply_markup=await get_menu_keyboard(update.effective_user.id),
    )


@logger_decor
@delete_previous_message
async def set_mailing(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Включение/выключение подписки пользователя на почтовую рассылку."""
    telegram_id = update.effective_user.id
    user_service = UserService()
    has_mailing = await user_service.set_mailing(telegram_id)
    if has_mailing:
        text = "Отлично! Теперь я буду присылать тебе уведомления о новых заданиях на почту."
        keyboard = await get_back_menu()
        parse_mode = ParseMode.MARKDOWN
    else:
        text = (
            "Ты больше не будешь получать новые задания от фондов, но всегда сможешь найти их на сайте "
            '<a href="https://procharity.ru">ProCharity</a>.\n\n'
            "Поделись, пожалуйста, почему ты решил отписаться?"
        )
        keyboard = get_no_mailing_keyboard()
        parse_mode = ParseMode.HTML
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text=text,
        reply_markup=keyboard,
        parse_mode=parse_mode,
        disable_web_page_preview=True,
    )


@logger_decor
async def reason(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    reason = enum.REASONS[context.match.group(1)]
    await log.ainfo(
        f"Пользователь {update.effective_user.username} ({update.effective_user.id}) отписался от "
        f"рассылки по причине: {reason}"
    )
    await query.message.edit_text(
        text="Спасибо, я передал информацию команде ProCharity!",
        reply_markup=await get_back_menu(),
        parse_mode=ParseMode.MARKDOWN,
    )


@logger_decor
async def ask_your_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


@logger_decor
@delete_previous_message
async def about_project(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="С ProCharity профессионалы могут помочь некоммерческим "
        "организациям в вопросах, которые требуют специальных знаний и "
        "опыта.\n\nИнтеллектуальный волонтёр безвозмездно дарит фонду своё "
        "время и профессиональные навыки, позволяя решать задачи, "
        "которые трудно закрыть силами штатных сотрудников.\n\n"
        'Сделано студентами <a href="https://praktikum.yandex.ru/">Яндекс.Практикума.</a>',
        reply_markup=await get_back_menu(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.MENU, menu_callback))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern=callback_data.MENU))
    app.add_handler(CallbackQueryHandler(ask_your_question, pattern=callback_data.ASK_YOUR_QUESTION))
    app.add_handler(CallbackQueryHandler(about_project, pattern=callback_data.ABOUT_PROJECT))
    app.add_handler(CallbackQueryHandler(ask_your_question, pattern=callback_data.SEND_ERROR_OR_PROPOSAL))
    app.add_handler(MessageHandler(StatusUpdate.WEB_APP_DATA, web_app_data))
    app.add_handler(CallbackQueryHandler(set_mailing, pattern=callback_data.JOB_SUBSCRIPTION))
    app.add_handler(CallbackQueryHandler(reason, pattern=patterns.NO_MAILING_REASON))
