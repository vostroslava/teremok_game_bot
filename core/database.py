import aiosqlite
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
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
        
        # User contacts table with status and notes
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
                status TEXT DEFAULT 'new',
                notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Test results table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS test_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                result_type TEXT NOT NULL,
                scores TEXT,
                answers TEXT,
                product TEXT DEFAULT 'teremok',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_contacts(user_id)
            )
        """)
        
        # Admins table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                role TEXT DEFAULT 'admin',
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration: add status and notes columns if they don't exist
        try:
            await db.execute("ALTER TABLE user_contacts ADD COLUMN status TEXT DEFAULT 'new'")
        except:
            pass
        try:
            await db.execute("ALTER TABLE user_contacts ADD COLUMN notes TEXT")
        except:
            pass
        try:
            await db.execute("ALTER TABLE user_contacts ADD COLUMN product TEXT DEFAULT 'teremok'")
        except:
            pass
        try:
            await db.execute("ALTER TABLE test_results ADD COLUMN scores TEXT")
        except:
            pass
        try:
            await db.execute("ALTER TABLE test_results ADD COLUMN product TEXT DEFAULT 'teremok'")
        except:
            pass
        
        await db.commit()

        # Formula RSP results table
        await db.execute("""
            CREATE TABLE IF NOT EXISTS formula_rsp_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                primary_type_code TEXT NOT NULL,
                primary_type_name TEXT NOT NULL,
                scores TEXT,
                answers TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES user_contacts(user_id)
            )
        """)

        # Web Admins table (Login/Password)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS web_admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                session_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Migration: add session_token if not exists
        try:
            await db.execute("ALTER TABLE web_admins ADD COLUMN session_token TEXT")
        except:
            pass
        
        # Check if default admin exists, if not create one
        # Default: admin / admin (Change immediately!)
        try:
             async with db.execute("SELECT 1 FROM web_admins") as cursor:
                 if not await cursor.fetchone():
                     salt = secrets.token_hex(16)
                     pwd_hash = hashlib.sha256(("admin" + salt).encode()).hexdigest()
                     await db.execute(
                         "INSERT INTO web_admins (username, password_hash, salt) VALUES (?, ?, ?)",
                         ("admin", pwd_hash, salt)
                     )
        except Exception:
             pass
        
        # Migration: add table if upgrading
        # (Already handled by IF NOT EXISTS, effectively)

        # ===== INDEXES (Optimization) =====
        await db.execute("CREATE INDEX IF NOT EXISTS idx_contacts_created ON user_contacts(created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_contacts_status ON user_contacts(status)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON user_contacts(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tests_created ON test_results(created_at)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tests_user_id ON test_results(user_id)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_tests_product ON test_results(product)")
        await db.execute("CREATE INDEX IF NOT EXISTS idx_formula_rsp_user ON formula_rsp_results(user_id)")
        
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

async def save_contact(user_id: int, name: str, role: str, company: str, 
                       team_size: str, phone: str, telegram_username: str = None,
                       product: str = 'teremok'):
    """Save or update user contact information"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute("""
            INSERT INTO user_contacts 
            (user_id, name, role, company, team_size, phone, telegram_username, product, updated_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, 'new')
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                role = excluded.role,
                company = excluded.company,
                team_size = excluded.team_size,
                phone = excluded.phone,
                telegram_username = excluded.telegram_username,
                product = excluded.product,
                updated_at = CURRENT_TIMESTAMP
        """, (user_id, name, role, company, team_size, phone, telegram_username, product))
        await db.commit()

async def get_contact(user_id: int) -> dict | None:
    """Get contact information for a user"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT * FROM user_contacts WHERE user_id = ?", (user_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def has_contact(user_id: int) -> bool:
    """Check if user has submitted contact info"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute(
            "SELECT 1 FROM user_contacts WHERE user_id = ?", (user_id,)
        ) as cursor:
            return await cursor.fetchone() is not None

async def save_test_result(user_id: int, result_type: str, answers: dict, 
                           scores: dict = None, product: str = 'teremok') -> int:
    """Save test result and return the ID"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        cursor = await db.execute(
            """INSERT INTO test_results (user_id, result_type, answers, scores, product)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, result_type, json.dumps(answers), json.dumps(scores or {}), product)
        )
        await db.commit()
        return cursor.lastrowid

async def save_formula_rsp_result(user_id: int, primary_code: str, primary_name: str, 
                                  scores: dict, answers: list) -> int:
    """Save Formula RSP test result"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        cursor = await db.execute(
            """INSERT INTO formula_rsp_results 
               (user_id, primary_type_code, primary_type_name, scores, answers)
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, primary_code, primary_name, json.dumps(scores), json.dumps(answers))
        )
        await db.commit()
        return cursor.lastrowid


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

async def create_web_admin(username: str, password: str):
    """Create a new web admin"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute(
            "INSERT INTO web_admins (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
        )
        await db.commit()

async def verify_web_admin(username: str, password: str) -> bool:
    """Verify web admin credentials"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute(
            "SELECT password_hash, salt FROM web_admins WHERE username = ?", 
            (username,)
        ) as cursor:
            row = await cursor.fetchone()
            if not row:
                return False
            
            stored_hash, salt = row
            input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return stored_hash == input_hash

async def set_web_admin_session(username: str, token: str):
    """Set session token for admin"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        await db.execute(
            "UPDATE web_admins SET session_token = ? WHERE username = ?",
            (token, username)
        )
        await db.commit()

async def get_web_admin_by_token(token: str) -> str | None:
    """Get username by session token"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        async with db.execute(
            "SELECT username FROM web_admins WHERE session_token = ?", 
            (token,)
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else None

# ===== WEB ADMIN FUNCTIONS =====

async def get_all_leads_full(limit: int = 100, status: str = None, 
                              search: str = None, days: int = None,
                              sort_by: str = "created_at", sort_order: str = "desc") -> list:
    """Get leads with full info, filters, search and sorting"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        
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
            conditions.append("c.status = ?")
            params.append(status)
        
        if days:
            date_from = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("c.created_at >= ?")
            params.append(date_from)
        
        if search:
            conditions.append("(c.name LIKE ? OR c.company LIKE ? OR c.phone LIKE ?)")
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
        
        query += f" ORDER BY {sort_col} {order} LIMIT ?"
        params.append(limit)
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_all_tests_full(limit: int = 100, product: str = None,
                              result_type: str = None, days: int = None,
                              sort_by: str = "created_at", sort_order: str = "desc") -> list:
    """Get test results with contact info and sorting"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        db.row_factory = aiosqlite.Row
        
        query = """
            SELECT t.*, 
                   c.name, c.role, c.company, c.team_size, c.phone, c.telegram_username
            FROM test_results t
            LEFT JOIN user_contacts c ON t.user_id = c.user_id
        """
        conditions = []
        params = []
        
        if product and product != 'all':
            conditions.append("t.product = ?")
            params.append(product)
        
        if result_type and result_type != 'all':
            conditions.append("t.result_type = ?")
            params.append(result_type)
        
        if days:
            date_from = (datetime.now() - timedelta(days=days)).isoformat()
            conditions.append("t.created_at >= ?")
            params.append(date_from)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        # Sorting whitelist
        sort_columns = {
            "created_at": "t.created_at",
            "result_type": "t.result_type",
            "product": "t.product",
            "name": "c.name",
            "company": "c.company",
            "role": "c.role"
        }
        
        sort_col = sort_columns.get(sort_by, "t.created_at")
        order = "ASC" if sort_order and sort_order.lower() == "asc" else "DESC"
        
        query += f" ORDER BY {sort_col} {order} LIMIT ?"
        params.append(limit)
        
        async with db.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def update_lead_status(user_id: int, status: str, notes: str = None):
    """Update lead status and notes"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        if notes is not None:
            await db.execute(
                "UPDATE user_contacts SET status = ?, notes = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (status, notes, user_id)
            )
        else:
            await db.execute(
                "UPDATE user_contacts SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (status, user_id)
            )
        await db.commit()

async def get_stats(days: int = None) -> dict:
    """Get statistics for admin dashboard"""
    async with aiosqlite.connect(settings.DB_NAME) as db:
        stats = {}
        
        # Total counts
        async with db.execute("SELECT COUNT(*) FROM user_contacts") as cursor:
            stats['total_leads'] = (await cursor.fetchone())[0]
        
        async with db.execute("SELECT COUNT(*) FROM test_results") as cursor:
            stats['total_tests'] = (await cursor.fetchone())[0]
        
        # Counts by status
        async with db.execute(
            "SELECT status, COUNT(*) FROM user_contacts GROUP BY status"
        ) as cursor:
            stats['leads_by_status'] = {row[0] or 'new': row[1] for row in await cursor.fetchall()}
        
        # Counts by product
        async with db.execute(
            "SELECT product, COUNT(*) FROM user_contacts GROUP BY product"
        ) as cursor:
            stats['leads_by_product'] = {row[0] or 'teremok': row[1] for row in await cursor.fetchall()}
        
        async with db.execute(
            "SELECT product, COUNT(*) FROM test_results GROUP BY product"
        ) as cursor:
            stats['tests_by_product'] = {row[0] or 'teremok': row[1] for row in await cursor.fetchall()}
        
        # Last 7 days
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        async with db.execute(
            "SELECT COUNT(*) FROM user_contacts WHERE created_at >= ?", (week_ago,)
        ) as cursor:
            stats['leads_7d'] = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM test_results WHERE created_at >= ?", (week_ago,)
        ) as cursor:
            stats['tests_7d'] = (await cursor.fetchone())[0]
        
        # Today
        today = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        async with db.execute(
            "SELECT COUNT(*) FROM user_contacts WHERE created_at >= ?", (today,)
        ) as cursor:
            stats['leads_today'] = (await cursor.fetchone())[0]
        
        async with db.execute(
            "SELECT COUNT(*) FROM test_results WHERE created_at >= ?", (today,)
        ) as cursor:
            stats['tests_today'] = (await cursor.fetchone())[0]
        
        return stats

async def get_recent_leads(limit: int = 10) -> list:
    """Get recent leads for dashboard"""
    return await get_all_leads_full(limit=limit)

async def get_recent_tests(limit: int = 10) -> list:
    """Get recent tests for dashboard"""
    return await get_all_tests_full(limit=limit)

# Legacy compatibility
async def get_all_leads(limit: int = 20) -> list:
    """Get recent leads (contacts) for admin panel"""
    return await get_all_leads_full(limit=limit)

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
