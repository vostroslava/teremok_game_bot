from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import InlineKeyboardButton, KeyboardButton, WebAppInfo, ReplyKeyboardMarkup, InlineKeyboardMarkup
from core.texts import TYPES_DATA
from core.config import settings

def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 О тренинге «Теремок»", callback_data="about_teremok"))
    builder.row(InlineKeyboardButton(text="👥 Типажи сотрудников", callback_data="types_menu"))
    builder.row(InlineKeyboardButton(text="🧩 Мини-диагностика", callback_data="start_diagnostic"))
    
    # Web App Button
    web_app_url = settings.WEB_APP_URL if settings.WEB_APP_URL else "https://google.com" # Fallback if not set
    builder.row(InlineKeyboardButton(text="🌐 Открыть Веб-версию", web_app=WebAppInfo(url=web_app_url)))
    
    builder.row(InlineKeyboardButton(text="📞 Связаться с человеком", callback_data="contact_form"))
    return builder.as_markup()

def types_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    # Generate buttons for each type
    for type_id, data in TYPES_DATA.items():
        builder.button(text=f"{data.emoji} {data.name_ru}", callback_data=f"type_{type_id}")
    builder.adjust(2) # 2 columns
    builder.row(InlineKeyboardButton(text="⬅ Назад", callback_data="main_menu"))
    return builder.as_markup()

def type_details_keyboard(type_id: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="💡 Пример ситуации", callback_data=f"example_{type_id}"))
    builder.row(InlineKeyboardButton(text="⬅ К типажам", callback_data="types_menu"))
    builder.row(InlineKeyboardButton(text="🏠 В меню", callback_data="main_menu"))
    return builder.as_markup()

def back_to_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🏠 В главное меню", callback_data="main_menu"))
    return builder.as_markup()

def diagnostics_keyboard(question_id: int, options: list) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for i, option in enumerate(options):
        # We pass index of option to save space in callback_data
        builder.button(text=option['text'][:30] + "...", callback_data=f"ans_{question_id}_{i}")
    builder.adjust(1)
    builder.row(InlineKeyboardButton(text="❌ Прервать", callback_data="main_menu"))
    return builder.as_markup()
