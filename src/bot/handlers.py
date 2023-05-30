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
from telegram.constants import ParseMode
from telegram.ext import CallbackContext, ContextTypes

from src.bot.constants import callback_data, commands
from src.bot.keyboards import MENU_KEYBOARD, get_categories_keyboard, get_subcategories_keyboard
from src.core.services.user import UserService
from src.settings import settings


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
                    callback_data=commands.GREETING,
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


async def menu_callback(update: Update, context: CallbackContext):
    """Create button menu."""
    keyboard = MENU_KEYBOARD
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери, что тебя интересует:", reply_markup=reply_markup)


async def categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_service = UserService()
    categories = await user_service.get_user_categories(update.effective_user.id)
    context.user_data["selected_categories"] = {category: None for category in categories}
    context.user_data["parent_id"] = None
    await update.message.reply_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_categories_keyboard(),
    )


async def ask_your_question(update: Update, context: CallbackContext):
    name = update.effective_chat["first_name"]
    surname = update.effective_chat["last_name"]
    text = "Задать вопрос"
    params = {"name": name, "surname": surname}
    if update.effective_message.web_app_data:
        text = "Исправить неверно внесенные данные"
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Нажмите на кнопку ниже, чтобы задать вопрос.",
        reply_markup=ReplyKeyboardMarkup.from_button(
            KeyboardButton(
                text=text,
                web_app=WebAppInfo(url=f"{settings.feedback_form_template_url}?{urllib.parse.urlencode(params)}"),
            )
        ),
    )


async def web_app_data(update: Update):
    user_data = json.loads(update.effective_message.web_app_data.data)
    buttons = [
        [InlineKeyboardButton(text="Открыть в меню", callback_data=callback_data.MENU)],
        [InlineKeyboardButton(text="Посмотреть открытые задания", callback_data=callback_data.VIEW_TASKS)],
    ]
    keyboard = InlineKeyboardMarkup(buttons)
    await update.message.reply_text(
        text=f"Спасибо, я передал информацию команде ProCharity!" f"Ответ придет на почту {user_data['email']}",
        reply_markup=ReplyKeyboardRemove(),
    )
    await update.message.reply_text(
        text="Вы можете вернуться в меню или посмотреть открытые задания. Нажмите на нужную кнопку.",
        reply_markup=keyboard,
    )


async def subcategories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    parent_id = int(context.match.group(1))
    context.user_data["parent_id"] = parent_id

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, context),
    )


async def select_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    subcategory_id = int(context.match.group(1))
    selected_categories = context.user_data.setdefault("selected_categories", {})

    if subcategory_id not in selected_categories:
        selected_categories[subcategory_id] = None
    else:
        del selected_categories[subcategory_id]

    parent_id = context.user_data["parent_id"]

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_subcategories_keyboard(parent_id, context),
    )


async def back_subcategory_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.message.edit_text(
        "Чтобы я знал, с какими задачами ты готов помогать, "
        "выбери свои профессиональные компетенции (можно выбрать "
        'несколько). После этого, нажми на пункт "Готово 👌"',
        reply_markup=await get_categories_keyboard(),
    )


async def confirm_categories_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Записывает выбранные категории в базу данных и отправляет пользователю отчет о выбранных категориях."""
    query = update.callback_query
    telegram_id = update.effective_user.id
    user_service = UserService()

    users_categories_ids = context.user_data.get("selected_categories", {}).keys()

    await user_service.set_categories_to_user(
        telegram_id=telegram_id,
        categories_ids=users_categories_ids,
    )

    categories = await user_service.get_user_categories(telegram_id)
    if not categories:
        await query.message.edit_text(text="Категории не выбраны.")
    else:
        await query.message.edit_text(
            text="Отлично! Теперь я буду присылать тебе уведомления о новых "
            f"заданиях в категориях: *{', '.join(categories.values())}*.\n\n",
            parse_mode=ParseMode.MARKDOWN,
        )
