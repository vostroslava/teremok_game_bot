from .base import BaseRepository
from models.user import User, UserContact, Admin, WebAdmin
from typing import Optional, List
import json
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class UserRepository(BaseRepository):
    
    # Telegram Users
    async def add_user(self, user: User) -> None:
        await self.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            user.user_id, user.username, user.first_name
        )

    # Contacts/Leads
    async def save_lead(self, user_id: int, contact_info: str, message: str) -> None:
        await self.execute(
            "INSERT INTO leads (user_id, contact_info, message) VALUES ($1, $2, $3)",
            user_id, contact_info, message
        )

    async def save_contact(self, contact: UserContact) -> None:
        await self.execute("""
            INSERT INTO user_contacts 
            (user_id, name, role, company, team_size, phone, telegram_username, product, updated_at, status, notes)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, CURRENT_TIMESTAMP, $9, $10)
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                role = excluded.role,
                company = excluded.company,
                team_size = excluded.team_size,
                phone = excluded.phone,
                telegram_username = excluded.telegram_username,
                product = excluded.product,
                updated_at = CURRENT_TIMESTAMP
        """, 
            contact.user_id, contact.name, contact.role, contact.company, 
            contact.team_size, contact.phone, contact.telegram_username, 
            contact.product, contact.status, contact.notes
        )

    async def get_contact(self, user_id: int) -> Optional[UserContact]:
        row = await self.fetch_one("SELECT * FROM user_contacts WHERE user_id = $1", user_id)
        if row:
            data = dict(row)
            return UserContact(**data)
        return None

    async def has_contact(self, user_id: int) -> bool:
        val = await self.fetch_val("SELECT 1 FROM user_contacts WHERE user_id = $1", user_id)
        return val is not None

    async def update_status(self, user_id: int, status: str, notes: str = None) -> None:
        if notes is not None:
            await self.execute(
                "UPDATE user_contacts SET status = $1, notes = $2, updated_at = CURRENT_TIMESTAMP WHERE user_id = $3",
                status, notes, user_id
            )
        else:
            await self.execute(
                "UPDATE user_contacts SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE user_id = $2",
                status, user_id
            )

    # Web Admins
    async def get_web_admin_by_username(self, username: str) -> Optional[WebAdmin]:
        row = await self.fetch_one("SELECT * FROM web_admins WHERE username = $1", username)
        return WebAdmin(**dict(row)) if row else None

    async def get_web_admin_by_token(self, token: str) -> Optional[WebAdmin]:
        row = await self.fetch_one("SELECT * FROM web_admins WHERE session_token = $1", token)
        return WebAdmin(**dict(row)) if row else None

    async def create_web_admin(self, admin: WebAdmin) -> None:
        await self.execute(
            "INSERT INTO web_admins (username, password_hash, salt) VALUES ($1, $2, $3)",
            admin.username, admin.password_hash, admin.salt
        )

    async def set_session_token(self, username: str, token: str) -> None:
        await self.execute(
            "UPDATE web_admins SET session_token = $1 WHERE username = $2",
            token, username
        )

    # Telegram Admins
    async def add_telegram_admin(self, user_id: int, username: str, role: str = 'admin', added_by: int = 0) -> None:
        await self.execute(
            "INSERT INTO admins (user_id, username, role, added_by) VALUES ($1, $2, $3, $4) ON CONFLICT(user_id) DO UPDATE SET role = EXCLUDED.role",
            user_id, username, role, added_by
        )

    async def remove_telegram_admin(self, user_id: int) -> None:
        await self.execute("DELETE FROM admins WHERE user_id = $1", user_id)

    async def get_telegram_admin(self, user_id: int) -> Optional[dict]:
        row = await self.fetch_one("SELECT * FROM admins WHERE user_id = $1", user_id)
        return dict(row) if row else None

    async def get_all_telegram_admins(self) -> List[dict]:
        rows = await self.fetch_all("SELECT * FROM admins")
        return [dict(row) for row in rows]
    
    async def is_telegram_admin(self, user_id: int) -> bool:
        val = await self.fetch_val("SELECT 1 FROM admins WHERE user_id = $1", user_id)
        return val is not None

    # Statistics
    async def get_statistics(self, days: int = None) -> dict:
        stats = {}
        
        # Total counts
        stats['total_leads'] = await self.fetch_val("SELECT COUNT(*) FROM user_contacts")
        stats['total_tests'] = await self.fetch_val("SELECT COUNT(*) FROM test_results")
        
        # Counts by status
        stats['new_leads'] = await self.fetch_val("SELECT COUNT(*) FROM user_contacts WHERE status = 'new'")
        stats['completed_leads'] = await self.fetch_val("SELECT COUNT(*) FROM user_contacts WHERE status = 'done'")
        
        # Recent activity (7 days)
        date_7d = datetime.now() - timedelta(days=7)
        
        stats['leads_7d'] = await self.fetch_val(
            "SELECT COUNT(*) FROM user_contacts WHERE created_at >= $1", date_7d
        )
        
        stats['tests_7d'] = await self.fetch_val(
            "SELECT COUNT(*) FROM test_results WHERE created_at >= $1", date_7d
        )
        
        # Today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stats['leads_today'] = await self.fetch_val(
            "SELECT COUNT(*) FROM user_contacts WHERE created_at >= $1", today
        )
        
        stats['tests_today'] = await self.fetch_val(
            "SELECT COUNT(*) FROM test_results WHERE created_at >= $1", today
        )
        
        return stats

    async def get_daily_statistics(self, days: int = 7) -> dict:
        """Get daily stats for charts"""
        
        today = datetime.now().date()
        dates = [(today - timedelta(days=i)).isoformat() for i in range(days-1, -1, -1)]
        
        # Prepare result structure
        result = {
            "labels": [d[5:] for d in dates], # MM-DD
            "leads": [],
            "tests": []
        }
        
        for date_str in dates:
            # We need datetime objects for asyncpg if column is timestamp
            # But here we are comparing created_at (timestamp) with date strings?
            # Postgres can cast string to timestamp.
            # Ideally:
            d_start = datetime.strptime(date_str, "%Y-%m-%d")
            d_end = d_start + timedelta(days=1)
            
            leads_count = await self.fetch_val(
                "SELECT COUNT(*) FROM user_contacts WHERE created_at >= $1 AND created_at < $2",
                d_start, d_end
            )
            
            tests_count = await self.fetch_val(
                "SELECT COUNT(*) FROM test_results WHERE created_at >= $1 AND created_at < $2",
                d_start, d_end
            )
            
            result["leads"].append(leads_count)
            result["tests"].append(tests_count)
            
        return result

    async def get_all_leads_full(self, limit: int = 100, status: str = None,
                                  search: str = None, days: int = None,
                                  sort_by: str = "created_at", sort_order: str = "desc") -> list:
        """Get leads with full info, filters, search and sorting"""
        
        query = """
            SELECT c.*, 
                   t.result_type, t.scores as test_scores, t.created_at as test_date,
                   t.id as test_id
            FROM user_contacts c 
            LEFT JOIN test_results t ON c.user_id = t.user_id
        """
        conditions = []
        params = []
        
        if status and status != 'all':
            conditions.append(f"c.status = ${len(params) + 1}")
            params.append(status)
        
        if days:
            date_from = datetime.now() - timedelta(days=days)
            conditions.append(f"c.created_at >= ${len(params) + 1}")
            params.append(date_from)
        
        if search:
            conditions.append(f"(c.name ILIKE ${len(params) + 1} OR c.company ILIKE ${len(params) + 2} OR c.phone ILIKE ${len(params) + 3})")
            search_term = f"%{search}%"
            params.extend([search_term, search_term, search_term])
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        # Sorting whitelist
        sort_columns = {
            "created_at": "c.created_at",
            "updated_at": "c.updated_at",
            "status": "c.status",
            "name": "c.name",
            "company": "c.company",
            "role": "c.role",
            "product": "c.product",
            "team_size": "c.team_size"
        }
        
        sort_col = sort_columns.get(sort_by, "c.created_at")
        order = "ASC" if sort_order and sort_order.lower() == "asc" else "DESC"
        
        query += f" ORDER BY {sort_col} {order} LIMIT ${len(params) + 1}"
        params.append(limit)
        
        rows = await self.fetch_all(query, *params)
        return [dict(row) for row in rows]

    async def get_recent_leads_full(self, limit: int = 10) -> list:
        """Get recent leads for dashboard"""
        return await self.get_all_leads_full(limit=limit)
