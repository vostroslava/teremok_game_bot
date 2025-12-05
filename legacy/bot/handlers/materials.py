from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, CallbackQueryHandler, MessageHandler, filters

from bot.resources import (
    MATERIALS_INTRO, 
    MATERIALS_DATA, 
    MATERIALS_KEYBOARD,
    BTN_MATERIALS
)

async def show_materials_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает меню материалов."""
    await update.message.reply_text(
        text=MATERIALS_INTRO,
        reply_markup=MATERIALS_KEYBOARD,
        parse_mode="Markdown"
    )

async def handle_material_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает выбранный материал."""
    query = update.callback_query
    await query.answer()
    
    material_key = query.data.replace("mat_", "")
    material = MATERIALS_DATA.get(material_key)
    
    if material:
        # Кнопка "Читать подробнее"
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📖 Читать полностью", url=material["link"])],
            [InlineKeyboardButton("🔙 К списку тем", callback_data="mat_back")]
        ])
        
        await query.edit_message_text(
            text=material["text"],
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
    elif material_key == "back":
        await query.edit_message_text(
            text=MATERIALS_INTRO,
            reply_markup=MATERIALS_KEYBOARD,
            parse_mode="Markdown"
        )

# Хендлеры для регистрации
materials_handlers = [
    MessageHandler(filters.Regex(f"^{BTN_MATERIALS}$"), show_materials_menu),
    CallbackQueryHandler(handle_material_selection, pattern="^mat_")
]
