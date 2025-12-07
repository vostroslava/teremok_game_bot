from .base import BaseRepository
from models.user import User, UserContact, Admin, WebAdmin
from typing import Optional, List
import json
import logging

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    
    # Telegram Users
    async def add_user(self, user: User) -> None:
        await self.execute(
            "INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
            (user.user_id, user.username, user.first_name)
        )

    # Contacts/Leads
    async def save_lead(self, user_id: int, contact_info: str, message: str) -> None:
        await self.execute(
            "INSERT INTO leads (user_id, contact_info, message) VALUES (?, ?, ?)",
            (user_id, contact_info, message)
        )

    async def save_contact(self, contact: UserContact) -> None:
        await self.execute("""
            INSERT INTO user_contacts 
            (user_id, name, role, company, team_size, phone, telegram_username, product, updated_at, status, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                role = excluded.role,
                company = excluded.company,
                team_size = excluded.team_size,
                phone = excluded.phone,
                telegram_username = excluded.telegram_username,
                product = excluded.product,
                updated_at = CURRENT_TIMESTAMP
        """, (
            contact.user_id, contact.name, contact.role, contact.company, 
            contact.team_size, contact.phone, contact.telegram_username, 
            contact.product, contact.status, contact.notes
        ))

    async def get_contact(self, user_id: int) -> Optional[UserContact]:
        row = await self.fetch_one("SELECT * FROM user_contacts WHERE user_id = ?", (user_id,))
        if row:
            data = dict(row)
            # Handle potential nulls or extra fields if needed
            return UserContact(**data)
        return None

    async def has_contact(self, user_id: int) -> bool:
        row = await self.fetch_one("SELECT 1 FROM user_contacts WHERE user_id = ?", (user_id,))
        return row is not None

    async def update_status(self, user_id: int, status: str, notes: str = None) -> None:
        if notes is not None:
            await self.execute(
                "UPDATE user_contacts SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (status, notes, user_id)
            )
        else:
            await self.execute(
                "UPDATE user_contacts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (status, user_id)
            )

    # Web Admins
    async def get_web_admin_by_username(self, username: str) -> Optional[WebAdmin]:
        row = await self.fetch_one("SELECT * FROM web_admins WHERE username = ?", (username,))
        return WebAdmin(**dict(row)) if row else None

    async def get_web_admin_by_token(self, token: str) -> Optional[WebAdmin]:
        row = await self.fetch_one("SELECT * FROM web_admins WHERE session_token = ?", (token,))
        return WebAdmin(**dict(row)) if row else None

    async def create_web_admin(self, admin: WebAdmin) -> None:
        await self.execute(
            "INSERT INTO web_admins (username, password_hash, salt) VALUES (?, ?, ?)",
            (admin.username, admin.password_hash, admin.salt)
        )

    async def set_session_token(self, username: str, token: str) -> None:
        await self.execute(
            "UPDATE web_admins SET session_token = ? WHERE username = ?",
            (token, username)
        )
