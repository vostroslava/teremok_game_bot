
from aiogram import Bot, Dispatcher
import logging
import asyncio
from core.config import settings
from bot.handlers import common, materials, diagnostics, lead_form, admin
from core.database import ensure_db_exists
from core.logging_config import setup_logging
from contextlib import asynccontextmanager

import uvicorn
from web.routes import app as web_app

# Setup logging
setup_logging(log_level="INFO", log_file="teremok.log")
logger = logging.getLogger(__name__)

async def start_bot(bot: Bot, dp: Dispatcher):
    print("🤖 Бот запускается...")
    # Include routers
    dp.include_router(admin.router)  # Admin commands first
    dp.include_router(common.router)
    dp.include_router(lead_form.router)
    
    # Pass bot instance to web routes for notifications
    from web.routes import set_bot
    set_bot(bot)
    
    await dp.start_polling(bot)

async def start_web():
    config = uvicorn.Config(web_app, host=settings.HOST, port=settings.PORT, log_level="info", reload=True)
    server = uvicorn.Server(config)
    print(f"🌍 Web App запускается на http://{settings.HOST}:{settings.PORT}")
    await server.serve()

async def main():
    logging.basicConfig(level=logging.INFO)
    
    # Init DB
    await ensure_db_exists()
    
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()
    
    # Run both
    await asyncio.gather(
        start_bot(bot, dp),
        start_web()
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
