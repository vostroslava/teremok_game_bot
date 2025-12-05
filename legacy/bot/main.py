import logging
from telegram.ext import ApplicationBuilder

from bot.config import TELEGRAM_TOKEN, LOG_LEVEL, LOG_FORMAT

# Настройка логирования
logging.basicConfig(
    format=LOG_FORMAT,
    level=LOG_LEVEL
)
logger = logging.getLogger(__name__)

def main():
    """Запуск бота."""
    if TELEGRAM_TOKEN == "YOUR_TOKEN_HERE":
        logger.error("Токен не задан! Укажите TELEGRAM_TOKEN в bot/config.py или в переменных окружения.")
        return

    logger.info("Запуск бота...")
    
    # Создание приложения
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Регистрация хендлеров
    from telegram.ext import CommandHandler, MessageHandler, filters
    from bot.handlers.common import start, handle_menu_buttons
    from bot.handlers.diagnostics import diagnostics_handler

    app.add_handler(CommandHandler("start", start))
    
    # Диалоги (должны быть перед обычными MessageHandler)
    app.add_handler(diagnostics_handler)
    
    # Материалы
    from bot.handlers.materials import materials_handlers
    for handler in materials_handlers:
        app.add_handler(handler)
        
    # Квизы
    from bot.handlers.quiz import quiz_handler
    app.add_handler(quiz_handler)
    
    # Обработчик текстовых сообщений для меню
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_buttons))

    # Запуск polling
    app.run_polling()
    logger.info("Бот остановлен.")

if __name__ == "__main__":
    main()
