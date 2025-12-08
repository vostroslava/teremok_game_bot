import asyncpg
from core.config import settings
from core.exceptions import RepositoryError
from typing import Optional, List, Any, Dict
import logging

logger = logging.getLogger(__name__)

class BaseRepository:
    def __init__(self):
        self.db_url = settings.DATABASE_URL

    async def get_connection(self):
        return await asyncpg.connect(self.db_url)

    async def execute(self, query: str, *params) -> str:
        """Execute a query (INSERT, UPDATE, DELETE)"""
        try:
            conn = await self.get_connection()
            try:
                return await conn.execute(query, *params)
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"DB Execute Error: {e} | Query: {query}")
            raise RepositoryError(f"Database error: {str(e)}")

    async def fetch_one(self, query: str, *params) -> Optional[asyncpg.Record]:
        try:
            conn = await self.get_connection()
            try:
                return await conn.fetchrow(query, *params)
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"DB Fetch One Error: {e} | Query: {query}")
            raise RepositoryError(f"Database error: {str(e)}")

    async def fetch_all(self, query: str, *params) -> List[asyncpg.Record]:
        try:
            conn = await self.get_connection()
            try:
                return await conn.fetch(query, *params)
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"DB Fetch All Error: {e} | Query: {query}")
            raise RepositoryError(f"Database error: {str(e)}")
            
    async def fetch_val(self, query: str, *params) -> Any:
        try:
            conn = await self.get_connection()
            try:
                return await conn.fetchval(query, *params)
            finally:
                await conn.close()
        except Exception as e:
            logger.error(f"DB Fetch Val Error: {e} | Query: {query}")
            raise RepositoryError(f"Database error: {str(e)}")
