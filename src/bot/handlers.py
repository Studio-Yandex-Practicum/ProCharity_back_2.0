from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes
from src.bot.services.category import CategoryService

from src.bot import constants as bot_constants
from src.core.services.user import UserService


async def start_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
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
                    callback_data=bot_constants.COMMAND__GREETING,
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
    return bot_constants.GREETING


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Create button menu."""
    keyboard = [
        [InlineKeyboardButton("Посмотреть открытые задания", callback_data="view_tasks")],
        [InlineKeyboardButton("Изменить компетенции", callback_data="change_category")],
        [InlineKeyboardButton("Отправить предложение/ошибку", callback_data="send_error_or_proposal")],
        [InlineKeyboardButton("Задать свой вопрос", callback_data="ask_your_question")],
        [InlineKeyboardButton("О платформе", callback_data="about_project")],
        [InlineKeyboardButton("⏹️ Остановить / ▶️ включить подписку на задания", callback_data="job_subscription")],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери, что тебя интересует:", reply_markup=reply_markup)


async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    category_service = CategoryService()
    categories = await category_service.get_unarchived_parents()

    categories_buttons = [
        [InlineKeyboardButton(category.name, callback_data=f"category_{category.id}")] for category in categories]
    keyboard.extend(categories_buttons)

    keyboard.extend([
        [InlineKeyboardButton(
            "Нет моих компетенций 😕",
            callback_data="add_categories"
        )],
        [InlineKeyboardButton(
            "Готово 👌",
            callback_data="confirm_categories"
        )]])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        "несколько). После этого, нажми на пункт \"Готово 👌\"",
        reply_markup=reply_markup
    )


async def subcategories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    category_service = CategoryService()
    parent_id = int(update.callback_query.data.split('_')[1])
    subcategories = await category_service.get_unarchived_subcategories(parent_id)

    categories_buttons = [
        [InlineKeyboardButton(category.name, callback_data=f'category_{parent_id}')] for category in subcategories]
    keyboard.extend(categories_buttons)

    keyboard.append(
        [InlineKeyboardButton(
            "Назад ⬅️",
            callback_data="change_category"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.callback_query.message.edit_text(
        "Выберите категории",
        reply_markup=reply_markup
    )
