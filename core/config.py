import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    MANAGER_CHAT_ID: int = int(os.getenv("MANAGER_CHAT_ID", "0")) if os.getenv("MANAGER_CHAT_ID") else 0
    
    # Web App
    WEB_APP_URL: str = os.getenv("WEB_APP_URL", "https://vostroslava.github.io/teremok_game_bot/")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DB_NAME: str = os.getenv("DB_NAME", "teremok.db")
    
    # Channel subscription check
    REQUIRED_CHANNEL_USERNAME: str = os.getenv("REQUIRED_CHANNEL_USERNAME", "testtesttest12332221")
    CHECK_SUBSCRIPTION_ENABLED: bool = os.getenv("CHECK_SUBSCRIPTION_ENABLED", "true").lower() == "true"

settings = Settings()
