import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Telegram Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    MANAGER_CHAT_ID: int = int(os.getenv("MANAGER_CHAT_ID", "0")) if os.getenv("MANAGER_CHAT_ID") else 0
    OWNER_ID: int = int(os.getenv("OWNER_ID", "0")) if os.getenv("OWNER_ID") else 0
    
    # Notifications (disable to avoid spam, admins can check via /leads)
    SEND_NOTIFICATIONS: bool = os.getenv("SEND_NOTIFICATIONS", "false").lower() == "true"
    
    # Web App
    WEB_APP_URL: str = os.getenv("WEB_APP_URL", "https://vostroslava.github.io/teremok_game_bot/")
    
    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database
    DB_TYPE: str = os.getenv("DB_TYPE", "postgres") # postgres or sqlite (legacy)
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "teremok")
    
    # Legacy/Fallback
    SQLITE_DB_NAME: str = os.getenv("DB_NAME", "teremok.db")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Channel subscription check
    REQUIRED_CHANNEL_USERNAME: str = os.getenv("REQUIRED_CHANNEL_USERNAME", "testtesttest12332221")
    CHECK_SUBSCRIPTION_ENABLED: bool = os.getenv("CHECK_SUBSCRIPTION_ENABLED", "true").lower() == "true"
    
    # Admin Panel
    ADMIN_PANEL_SECRET: str = os.getenv("ADMIN_PANEL_SECRET", "")
    
    # Google Sheets Integration (via Apps Script Webhook)
    GOOGLE_SHEETS_ENABLED: bool = os.getenv("GOOGLE_SHEETS_ENABLED", "false").lower() == "true"
    GOOGLE_SHEETS_WEBHOOK_URL: str = os.getenv("GOOGLE_SHEETS_WEBHOOK_URL", "")

settings = Settings()
