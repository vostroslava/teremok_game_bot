import asyncpg
import os
import json
import hashlib
import secrets
from datetime import datetime, timedelta
from .config import settings

async def ensure_db_exists():
    try:
        # Connect to default 'postgres' database to check if target DB exists
        # This part assumes we can connect to the server. 
        # For simplicity in this migration script, we assume the DB 'teremok' (or whatever in .env) ALREADY EXISTS
        # because creating a DB from within asyncpg requires connecting to 'postgres' db first.
        # User said "I downloaded it", implying they have a server. They should create the DB manually or we assume it exists.
        # We will just try to connect to the target DB and create tables.
        
        conn = await asyncpg.connect(settings.DATABASE_URL)
        try:
            # Users table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Leads table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS leads (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT,
                    contact_info TEXT,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User contacts table with status and notes
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS user_contacts (
                    user_id BIGINT PRIMARY KEY,
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
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS test_results (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    result_type TEXT NOT NULL,
                    scores TEXT,
                    answers TEXT,
                    product TEXT DEFAULT 'teremok',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_contacts(user_id)
                )
            """)
            
            # Admins table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS admins (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    role TEXT DEFAULT 'admin',
                    added_by BIGINT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Formula RSP results table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS formula_rsp_results (
                    id SERIAL PRIMARY KEY,
                    user_id BIGINT NOT NULL,
                    primary_type_code TEXT NOT NULL,
                    primary_type_name TEXT NOT NULL,
                    scores TEXT,
                    answers TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES user_contacts(user_id)
                )
            """)

            # Web Admins table (Login/Password)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS web_admins (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    session_token TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create default admin if not exists
            # Default: admin / admin
            exists = await conn.fetchval("SELECT 1 FROM web_admins LIMIT 1")
            if not exists:
                salt = secrets.token_hex(16)
                pwd_hash = hashlib.sha256(("admin" + salt).encode()).hexdigest()
                await conn.execute(
                    "INSERT INTO web_admins (username, password_hash, salt) VALUES ($1, $2, $3)",
                    "admin", pwd_hash, salt
                )
            
            # Indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_created ON user_contacts(created_at)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_status ON user_contacts(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_contacts_user_id ON user_contacts(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tests_created ON test_results(created_at)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tests_user_id ON test_results(user_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_tests_product ON test_results(product)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_formula_rsp_user ON formula_rsp_results(user_id)")

        finally:
            await conn.close()
    except Exception as e:
        print(f"DB Init Error: {e}")

async def add_user(user_id: int, username: str, first_name: str):
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute(
            "INSERT INTO users (user_id, username, first_name) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
            user_id, username, first_name
        )
    finally:
        await conn.close()

async def save_lead(user_id: int, contact_info: str, message: str):
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute(
            "INSERT INTO leads (user_id, contact_info, message) VALUES ($1, $2, $3)",
            user_id, contact_info, message
        )
    finally:
        await conn.close()

async def save_contact(user_id: int, name: str, role: str, company: str, 
                       team_size: str, phone: str, telegram_username: str = None,
                       product: str = 'teremok'):
    """Save or update user contact information"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute("""
            INSERT INTO user_contacts 
            (user_id, name, role, company, team_size, phone, telegram_username, product, updated_at, status)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, CURRENT_TIMESTAMP, 'new')
            ON CONFLICT(user_id) DO UPDATE SET
                name = excluded.name,
                role = excluded.role,
                company = excluded.company,
                team_size = excluded.team_size,
                phone = excluded.phone,
                telegram_username = excluded.telegram_username,
                product = excluded.product,
                updated_at = CURRENT_TIMESTAMP
        """, user_id, name, role, company, team_size, phone, telegram_username, product)
    finally:
        await conn.close()

async def get_contact(user_id: int) -> dict | None:
    """Get contact information for a user"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        row = await conn.fetchrow(
            "SELECT * FROM user_contacts WHERE user_id = $1", user_id
        )
        return dict(row) if row else None
    finally:
        await conn.close()

async def has_contact(user_id: int) -> bool:
    """Check if user has submitted contact info"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        val = await conn.fetchval(
            "SELECT 1 FROM user_contacts WHERE user_id = $1", user_id
        )
        return val is not None
    finally:
        await conn.close()

async def save_test_result(user_id: int, result_type: str, answers: dict, 
                            scores: dict = None, product: str = 'teremok') -> int:
    """Save test result and return the ID"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        # Postgres requires RETURNING id to get the inserted id
        val = await conn.fetchval(
            """INSERT INTO test_results (user_id, result_type, answers, scores, product)
               VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            user_id, result_type, json.dumps(answers), json.dumps(scores or {}), product
        )
        return val
    finally:
        await conn.close()

async def save_formula_rsp_result(user_id: int, primary_code: str, primary_name: str, 
                                  scores: dict, answers: list) -> int:
    """Save Formula RSP test result"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        val = await conn.fetchval(
            """INSERT INTO formula_rsp_results 
               (user_id, primary_type_code, primary_type_name, scores, answers)
               VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            user_id, primary_code, primary_name, json.dumps(scores), json.dumps(answers)
        )
        return val
    finally:
        await conn.close()


async def get_test_results(user_id: int) -> list:
    """Get all test results for a user"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        rows = await conn.fetch(
            "SELECT * FROM test_results WHERE user_id = $1 ORDER BY created_at DESC",
            user_id
        )
        return [dict(row) for row in rows]
    finally:
        await conn.close()

# ===== ADMIN FUNCTIONS =====

async def add_admin(user_id: int, username: str = None, role: str = 'admin', added_by: int = None):
    """Add a user as admin"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute(
            """INSERT INTO admins (user_id, username, role, added_by) VALUES ($1, $2, $3, $4)
               ON CONFLICT(user_id) DO UPDATE SET role = EXCLUDED.role""",
            user_id, username, role, added_by
        )
    finally:
        await conn.close()

async def remove_admin(user_id: int):
    """Remove admin rights from a user"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute("DELETE FROM admins WHERE user_id = $1", user_id)
    finally:
        await conn.close()

async def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        val = await conn.fetchval("SELECT 1 FROM admins WHERE user_id = $1", user_id)
        return val is not None
    finally:
        await conn.close()

async def get_admin_role(user_id: int) -> str | None:
    """Get admin role (owner/admin) or None if not admin"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        val = await conn.fetchval("SELECT role FROM admins WHERE user_id = $1", user_id)
        return val
    finally:
        await conn.close()

async def get_all_admins() -> list:
    """Get all admins"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        rows = await conn.fetch("SELECT * FROM admins ORDER BY added_at")
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def create_web_admin(username: str, password: str):
    """Create a new web admin"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute(
            "INSERT INTO web_admins (username, password_hash, salt) VALUES ($1, $2, $3)",
            username, password_hash, salt
        )
    finally:
        await conn.close()

async def verify_web_admin(username: str, password: str) -> bool:
    """Verify web admin credentials"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        row = await conn.fetchrow(
            "SELECT password_hash, salt FROM web_admins WHERE username = $1", 
            username
        )
        if not row:
            return False
        
        stored_hash = row['password_hash']
        salt = row['salt']
        input_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return stored_hash == input_hash
    finally:
        await conn.close()

async def set_web_admin_session(username: str, token: str):
    """Set session token for admin"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        await conn.execute(
            "UPDATE web_admins SET session_token = $1 WHERE username = $2",
            token, username
        )
    finally:
        await conn.close()

async def get_web_admin_by_token(token: str) -> str | None:
    """Get username by session token"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        val = await conn.fetchval(
            "SELECT username FROM web_admins WHERE session_token = $1", 
            token
        )
        return val
    finally:
        await conn.close()

# ===== WEB ADMIN FUNCTIONS =====

async def get_all_leads_full(limit: int = 100, status: str = None, 
                              search: str = None, days: int = None,
                              sort_by: str = "created_at", sort_order: str = "desc") -> list:
    """Get leads with full info, filters, search and sorting"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
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
            # Ensure it's passed as datetime object, asyncpg handles escaping
            conditions.append(f"c.created_at >= ${len(params) + 1}")
            params.append(date_from)
        
        if search:
            conditions.append(f"(c.name ILIKE ${len(params) + 1} OR c.company ILIKE ${len(params) + 2} OR c.phone ILIKE ${len(params) + 3})")
            search_term = f"%{search}%"
            # Postgres ILIKE is case insensitive like SQLite LIKE (sometimes).
            # SQLite LIKE is case insensitive for ASCII. Postgres LIKE is case sensitive. ILIKE is case insensitive.
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
        
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def get_all_tests_full(limit: int = 100, product: str = None,
                              result_type: str = None, days: int = None,
                              sort_by: str = "created_at", sort_order: str = "desc") -> list:
    """Get test results with contact info and sorting"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        query = """
            SELECT t.*, 
                   c.name, c.role, c.company, c.team_size, c.phone, c.telegram_username
            FROM test_results t
            LEFT JOIN user_contacts c ON t.user_id = c.user_id
        """
        conditions = []
        params = []
        
        if product and product != 'all':
            conditions.append(f"t.product = ${len(params) + 1}")
            params.append(product)
        
        if result_type and result_type != 'all':
            conditions.append(f"t.result_type = ${len(params) + 1}")
            params.append(result_type)
        
        if days:
            date_from = datetime.now() - timedelta(days=days)
            conditions.append(f"t.created_at >= ${len(params) + 1}")
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
        
        query += f" ORDER BY {sort_col} {order} LIMIT ${len(params) + 1}"
        params.append(limit)
        
        rows = await conn.fetch(query, *params)
        return [dict(row) for row in rows]
    finally:
        await conn.close()

async def update_lead_status(user_id: int, status: str, notes: str = None):
    """Update lead status and notes"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        if notes is not None:
            await conn.execute(
                "UPDATE user_contacts SET status = $1, notes = $2, updated_at = CURRENT_TIMESTAMP WHERE user_id = $3",
                status, notes, user_id
            )
        else:
            await conn.execute(
                "UPDATE user_contacts SET status = $1, updated_at = CURRENT_TIMESTAMP WHERE user_id = $2",
                status, user_id
            )
    finally:
        await conn.close()

async def get_stats(days: int = None) -> dict:
    """Get statistics for admin dashboard"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        stats = {}
        
        # Total counts
        stats['total_leads'] = await conn.fetchval("SELECT COUNT(*) FROM user_contacts")
        stats['total_tests'] = await conn.fetchval("SELECT COUNT(*) FROM test_results")
        
        # Counts by status
        rows = await conn.fetch("SELECT status, COUNT(*) FROM user_contacts GROUP BY status")
        stats['leads_by_status'] = {row['status'] or 'new': row['count'] for row in rows}
        
        # Counts by product
        rows = await conn.fetch("SELECT product, COUNT(*) FROM user_contacts GROUP BY product")
        stats['leads_by_product'] = {row['product'] or 'teremok': row['count'] for row in rows}
        
        rows = await conn.fetch("SELECT product, COUNT(*) FROM test_results GROUP BY product")
        stats['tests_by_product'] = {row['product'] or 'teremok': row['count'] for row in rows}
        
        # Last 7 days
        week_ago = datetime.now() - timedelta(days=7)
        stats['leads_7d'] = await conn.fetchval(
            "SELECT COUNT(*) FROM user_contacts WHERE created_at >= $1", week_ago
        )
        stats['tests_7d'] = await conn.fetchval(
            "SELECT COUNT(*) FROM test_results WHERE created_at >= $1", week_ago
        )
        
        # Today
        today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        stats['leads_today'] = await conn.fetchval(
            "SELECT COUNT(*) FROM user_contacts WHERE created_at >= $1", today
        )
        stats['tests_today'] = await conn.fetchval(
            "SELECT COUNT(*) FROM test_results WHERE created_at >= $1", today
        )
        
        return stats
    finally:
        await conn.close()

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
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        return await conn.fetchval("SELECT COUNT(*) FROM user_contacts")
    finally:
        await conn.close()

async def get_tests_count() -> int:
    """Get total number of completed tests"""
    conn = await asyncpg.connect(settings.DATABASE_URL)
    try:
        return await conn.fetchval("SELECT COUNT(*) FROM test_results")
    finally:
        await conn.close()
