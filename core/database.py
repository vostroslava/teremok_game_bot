import aiosqlite
import os
import json
from .config import settings

async def ensure_db_exists():
    async with aiosqlite.connect(settings.DB_NAME) as db:
        # Users table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Leads table (existing)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                contact_info TEXT,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # User contacts table (NEW)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_contacts (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                role TEXT NOT NULL,
                company TEXT,
                team_size TEXT NOT NULL,
                phone TEXT NOT NULL,
                telegram_username TEXT,
                product TEXT DEFAULT 'teremok',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Test results table (NEW)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                result_type TEXT NOT NULL,
                answers TEXT,
                product TEXT DEFAULT 'teremok',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_contacts(user_id)
            )
        """)
        
        # Admins table - for role-based access
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'admin',
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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

# ===== NEW CONTACT FUNCTIONS =====

async def save_contact(user_id: int, name: str, role: str, company: str, 
                       team_size: str, phone: str, telegram_username: str = None):
    """Save or update user contact information"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute("""
            INSERT OR REPLACE INTO user_contacts 
            (user_id, name, role, company, team_size, phone, telegram_username, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """, (user_id, name, role, company, team_size, phone, telegram_username))
        await db.commit()

async def get_contact(user_id: int) -> dict | None:
    """Get user contact information"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM user_contacts WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                return dict(row)
            return None

async def has_contact(user_id: int) -> bool:
    """Check if user has filled contact information"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute(
            "SELECT 1 FROM user_contacts WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row is not None

async def save_test_result(user_id: int, result_type: str, answers: dict):
    """Save test results"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        answers_json = json.dumps(answers, ensure_ascii=False)
        await db.execute(
            "INSERT INTO test_results (user_id, result_type, answers) VALUES (?, ?, ?)",
            (user_id, result_type, answers_json)
        )
        await db.commit()

async def get_test_results(user_id: int) -> list:
    """Get all test results for a user"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM test_results WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

# ===== ADMIN FUNCTIONS =====

async def add_admin(user_id: int, username: str = None, role: str = 'admin', added_by: int = None):
    """Add a user as admin"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute(
            "INSERT OR REPLACE INTO admins (user_id, username, role, added_by) VALUES (?, ?, ?, ?)",
            (user_id, username, role, added_by)
        )
        await db.commit()

async def remove_admin(user_id: int):
    """Remove admin rights from a user"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
        await db.commit()

async def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute(
            "SELECT 1 FROM admins WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone() is not None

async def get_admin_role(user_id: int) -> str | None:
    """Get admin role (owner/admin) or None if not admin"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute(
            "SELECT role FROM admins WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

async def get_all_admins() -> list:
    """Get all admins"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM admins ORDER BY added_at") as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_all_leads(limit: int = 20) -> list:
    """Get recent leads (contacts) for admin panel"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """SELECT c.*, t.result_type, t.created_at as test_date 
               FROM user_contacts c 
               LEFT JOIN test_results t ON c.user_id = t.user_id 
               ORDER BY c.created_at DESC 
               LIMIT ?""",
            (limit,)
        ) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_leads_count() -> int:
    """Get total number of leads"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM user_contacts") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0

async def get_tests_count() -> int:
    """Get total number of completed tests"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute("SELECT COUNT(*) FROM test_results") as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
