import aiosqlite
from core.config import settings
from core.exceptions import RepositoryError
from typing import Optional, List, Any, Dict
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self):
        self.db_name = settings.DB_NAME

    async def execute(self, query: str, params: tuple = ()) -> aiosqlite.Cursor:
        try:
            async with aiosqlite.connect(self.db_name) as db:
                cursor = await db.execute(query, params)
                await db.commit()
                return cursor
        except Exception as e:
            logger.error(f"DB Execute Error: {e} | Query: {query}")
            raise RepositoryError(f"Database error: {str(e)}")

    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[aiosqlite.Row]:
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    return await cursor.fetchone()
        except Exception as e:
            logger.error(f"DB Fetch One Error: {e} | Query: {query}")
            raise RepositoryError(f"Database error: {str(e)}")

    async def fetch_all(self, query: str, params: tuple = ()) -> List[aiosqlite.Row]:
        try:
            async with aiosqlite.connect(self.db_name) as db:
                db.row_factory = aiosqlite.Row
                async with db.execute(query, params) as cursor:
                    return await cursor.fetchall()
        except Exception as e:
            logger.error(f"DB Fetch All Error: {e} | Query: {query}")
            raise RepositoryError(f"Database error: {str(e)}")
