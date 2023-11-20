import structlog
from dependency_injector.wiring import Provide
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from src.bot.constants import callback_data, commands, enum, patterns
from src.bot.keyboards import get_back_menu, get_menu_keyboard, get_no_mailing_keyboard
from src.bot.services.unsubscribe_reason import UnsubscribeReasonService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message
from src.core.depends import Container
from src.core.logging.utils import logger_decor

log = structlog.get_logger()


@logger_decor
@delete_previous_message
async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    """Возвращает в меню."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери, что тебя интересует:",
        reply_markup=await get_menu_keyboard(await user_service.get_by_telegram_id(update.effective_user.id)),
    )


@logger_decor
@delete_previous_message
async def set_mailing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    """Включение/выключение подписки пользователя на почтовую рассылку."""
    telegram_id = update.effective_user.id
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
async def reason_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    unsubscribe_reason_service: UnsubscribeReasonService = Provide[
        Container.bot_services_container.unsubscribe_reason_service
    ],
):
    query = update.callback_query
    reason = enum.REASONS[context.match.group(1)]
    await unsubscribe_reason_service.save_reason(telegram_id=context._user_id, reason=reason)
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
    app.add_handler(CallbackQueryHandler(about_project, pattern=callback_data.ABOUT_PROJECT))
    app.add_handler(CallbackQueryHandler(set_mailing, pattern=callback_data.JOB_SUBSCRIPTION))
    app.add_handler(CallbackQueryHandler(reason_handler, pattern=patterns.NO_MAILING_REASON))
