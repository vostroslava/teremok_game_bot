import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    ADMIN_ID: int = int(os.getenv("ADMIN_ID", "0")) if os.getenv("ADMIN_ID") else None
    
    # Web App
    WEB_APP_URL: str = os.getenv("WEB_APP_URL", "")  # URL where the Web App is hosted
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DB_NAME: str = os.getenv("DB_NAME", "teremok.db")

settings = Settings()
