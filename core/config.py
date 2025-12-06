import os
from dotenv import load_dotenv

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # Telegram Bot
    BOT_TOKEN: str
    
    # Web App
    WEB_APP_URL: str = Field(default="https://vostroslava.github.io/teremok_game_bot/")
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    
    # Database
    DB_NAME: str = Field(default="teremok.db")
    
    # Manager notifications
    MANAGER_CHAT_ID: int = Field(default=0)
    
    # Channel subscription check
    REQUIRED_CHANNEL_USERNAME: str = Field(default="testtesttest12332221")
    CHECK_SUBSCRIPTION_ENABLED: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
```
