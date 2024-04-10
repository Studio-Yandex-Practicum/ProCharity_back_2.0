import asyncio

import structlog
from dependency_injector.wiring import Provide
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from src.bot.constants import callback_data, commands, enum, patterns
from src.bot.keyboards import (
    get_back_menu,
    get_menu_keyboard,
    get_no_mailing_keyboard,
    get_tasks_and_back_menu_keyboard,
    support_service_keyboard,
)
from src.bot.services.unsubscribe_reason import UnsubscribeReasonService
from src.bot.services.user import UserService
from src.bot.utils import delete_previous_message, registered_user_required
from src.core.db.models import ExternalSiteUser
from src.core.depends import Container
from src.core.logging.utils import logger_decor
from src.core.services.email import EmailProvider

log = structlog.get_logger()


@logger_decor
@registered_user_required
@delete_previous_message
async def menu_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
):
    """Возвращает в меню."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Выбери, что тебя интересует:",
        reply_markup=await get_menu_keyboard(ext_site_user.user),
    )


@logger_decor
@delete_previous_message
async def set_mailing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    procharity_tasks_url: str = Provide[Container.settings.provided.procharity_tasks_url],
):
    """Включение/выключение подписки пользователя на почтовую рассылку."""
    telegram_id = update.effective_user.id
    has_mailing = await user_service.get_mailing(telegram_id)
    if not has_mailing:
        await user_service.toggle_mailing(telegram_id)
        text = "*Подписка включена!*\n\nТеперь ты будешь получать новые задания от фондов по выбранным компетенциям."
        keyboard = await get_tasks_and_back_menu_keyboard()
        parse_mode = ParseMode.MARKDOWN
    else:
        text = (
            "<b>Подписка остановлена!</b>\n\n"
            "Ты больше не будешь получать новые задания от фондов, но всегда сможешь найти их в меню бота или "
            f'<a href="{procharity_tasks_url}">на сайте</a>.\n\n'
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
async def unsubscription_reason_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    unsubscribe_reason_service: UnsubscribeReasonService = Provide[
        Container.bot_services_container.unsubscribe_reason_service
    ],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
    email_admin: str = Provide[Container.settings.provided.EMAIL_ADMIN],
    email_provider: EmailProvider = Provide[Container.core_services_container.email_provider],
):
    """Выключение подписки пользователя и отправка сообщения с причиной на почту."""
    telegram_id = update.effective_user.id
    await user_service.toggle_mailing(telegram_id)
    query = update.callback_query
    reason = enum.REASONS[context.match.group(1)]
    await unsubscribe_reason_service.save_reason(telegram_id=context._user_id, reason=reason.name)
    background_task = email_provider.unsubscribe_notification(
        user_name=update.effective_user.username,
        user_id=update.effective_user.id,
        reason=reason,
        to_email=email_admin,
    )
    asyncio.create_task(background_task)
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
async def about_project(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ya_praktikum_url: str = Provide[Container.settings.provided.YA_PRAKTIKUM_URL],
):
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="С ProCharity профессионалы могут помочь некоммерческим "
        "организациям в вопросах, которые требуют специальных знаний и "
        "опыта.\n\nИнтеллектуальный волонтёр безвозмездно дарит фонду своё "
        "время и профессиональные навыки, позволяя решать задачи, "
        "которые трудно закрыть силами штатных сотрудников.\n\n"
        f'Сделано студентами <a href="{ya_praktikum_url}">Яндекс.Практикума.</a>',
        reply_markup=await get_back_menu(),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True,
    )


@logger_decor
@delete_previous_message
async def support_service_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    url: str = Provide[Container.settings.provided.procharity_faq_volunteer_url],
    user_service: UserService = Provide[Container.bot_services_container.bot_user_service],
):
    """Отправляет сервис меню."""
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Мы на связи с 10.00 до 19.00"
        "в будние дни по любым вопросам. Смело пиши нам!\n\n"
        "А пока мы изучаем твой запрос, можешь ознакомиться с"
        "популярными вопросами и ответами на них в нашей"
        f'<a href="{url}"> базе знаний.</a>',
        reply_markup=await support_service_keyboard(await user_service.get_by_telegram_id(update.effective_user.id)),
        parse_mode=ParseMode.HTML,
    )


def registration_handlers(app: Application):
    app.add_handler(CommandHandler(commands.MENU, menu_callback))
    app.add_handler(CallbackQueryHandler(menu_callback, pattern=callback_data.MENU))
    app.add_handler(CallbackQueryHandler(about_project, pattern=callback_data.ABOUT_PROJECT))
    app.add_handler(CallbackQueryHandler(set_mailing, pattern=callback_data.JOB_SUBSCRIPTION))
    app.add_handler(CallbackQueryHandler(unsubscription_reason_handler, pattern=patterns.NO_MAILING_REASON))
    app.add_handler(CallbackQueryHandler(support_service_callback, pattern=callback_data.SUPPORT_SERVICE))
