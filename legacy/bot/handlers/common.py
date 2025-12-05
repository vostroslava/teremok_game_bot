from telegram import Update
from telegram.ext import ContextTypes
from bot.resources import (
    WELCOME_TEXT, 
    ABOUT_TEXT, 
    MAIN_MENU_KEYBOARD,
    BTN_ABOUT
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start."""
    await update.message.reply_text(
        text=WELCOME_TEXT,
        reply_markup=MAIN_MENU_KEYBOARD,
        parse_mode="Markdown"
    )

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'О компании'."""
    await update.message.reply_text(
        text=ABOUT_TEXT,
        parse_mode="Markdown"
    )

async def handle_menu_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий кнопок главного меню."""
    text = update.message.text
    
    if text == BTN_ABOUT:
        await about(update, context)
    # Остальные кнопки будут обрабатываться в других модулях или здесь же
    # Пока заглушка для остальных
    elif text in [
        "📝 Диагностика команды", 
        "🎓 Полезные материалы", 
        "🏆 Квизы и Игры", 
        "📅 Мероприятия", 
        "💬 Консультант / FAQ"
    ]:
        await update.message.reply_text(f"Раздел '{text}' находится в разработке. 🛠")
    else:
        await update.message.reply_text("Неизвестная команда. Пожалуйста, воспользуйтесь меню.")
