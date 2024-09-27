from telegram import Update
from telegram.ext import Application, ContextTypes, MessageHandler, filters

from src.bot.utils import registered_user_required
from src.core.db.models import ExternalSiteUser
from src.core.logging.utils import logger_decor

ALLOWED_MESSAGES_FILTER = (
    filters.TEXT
    | filters.VOICE
    | filters.Document.ALL
    | filters.PHOTO
    | filters.VIDEO
    | filters.VIDEO_NOTE
    | filters.AUDIO
    | filters.Sticker.ALL
) & ~filters.ANIMATION

DISALLOWED_MESSAGES_FILTER = filters.LOCATION | filters.POLL | filters.CONTACT | filters.ANIMATION


@logger_decor
@registered_user_required
async def allowed_messages_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
):
    print(type(update.message.effective_attachment))
    filling = ("твои", "") if ext_site_user.user.is_volunteer else ("ваши", "те")
    text = (
        "Пока что мы не можем получать {} сообщения через бот — "
        "пожалуйста, пиши{} нам через форму обратной связи. "
        'Ее можно найти в меню бота по кнопке "✍ Написать в службу поддержки".'
    ).format(*filling)
    await update.effective_message.reply_text(text)


@logger_decor
@registered_user_required
async def disallowed_messages_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ext_site_user: ExternalSiteUser,
):
    filling = ("",) if ext_site_user.user.is_volunteer else ("те",)
    text = (
        "Такие сообщения бот не принимает — "
        "пожалуйста, пиши{} нам через форму обратной связи. "
        'Ее можно найти в меню бота по кнопке "✍ Написать в службу поддержки".'
    ).format(*filling)
    await update.effective_message.reply_text(text)


def registration_handlers(app: Application):
    app.add_handler(MessageHandler(ALLOWED_MESSAGES_FILTER, allowed_messages_callback))
    app.add_handler(MessageHandler(DISALLOWED_MESSAGES_FILTER, disallowed_messages_callback))
