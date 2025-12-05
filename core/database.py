import aiosqlite
import os
from .config import settings

async def ensure_db_exists():
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contact_info TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()

async def add_user(user_id: int, username: str, first_name: str):
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user_id, username, first_name)
        )
        await db.commit()

async def save_lead(user_id: int, contact_info: str, message: str):
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute(
            "INSERT INTO leads (user_id, contact_info, message) VALUES (?, ?, ?)",
            (user_id, contact_info, message)
        )
        await db.commit()
