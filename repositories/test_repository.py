from .base import BaseRepository
from models.test_result import TestResult, FormulaResult
from typing import Optional, List, Dict
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

class TestRepository(BaseRepository):
    
    async def save_test_result(self, result: TestResult) -> int:
        scores_json = json.dumps(result.scores) if isinstance(result.scores, dict) else result.scores
        answers_json = json.dumps(result.answers) if isinstance(result.answers, dict) else result.answers
        
        # Postgres requires RETURNING id
        val = await self.fetch_val(
            """INSERT INTO test_results (user_id, result_type, answers, scores, product)
               VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            result.user_id, result.result_type, answers_json, scores_json, result.product
        )
        return val

    async def save_formula_result(self, result: FormulaResult) -> int:
        scores_json = json.dumps(result.scores) if isinstance(result.scores, dict) else result.scores
        answers_json = json.dumps(result.answers) if isinstance(result.answers, (dict, list)) else result.answers
        
        val = await self.fetch_val(
            """INSERT INTO formula_rsp_results 
               (user_id, primary_type_code, primary_type_name, scores, answers)
               VALUES ($1, $2, $3, $4, $5) RETURNING id""",
            result.user_id, result.primary_type_code, result.primary_type_name, scores_json, answers_json
        )
        return val

    async def get_all_tests_full(self, limit: int = 100, product: str = None,
                                  result_type: str = None, days: int = None,
                                  sort_by: str = "created_at", sort_order: str = "desc") -> list:
        """Get test results with contact info and sorting"""
        
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
        
        rows = await self.fetch_all(query, *params)
        return [dict(row) for row in rows]

    async def get_recent_tests_full(self, limit: int = 10) -> list:
        """Get recent tests for dashboard"""
        return await self.get_all_tests_full(limit=limit)

    async def get_user_results(self, user_id: int) -> List[TestResult]:
        rows = await self.fetch_all(
            "SELECT * FROM test_results WHERE user_id = $1 ORDER BY created_at DESC",
            user_id
        )
        return [TestResult(**dict(row)) for row in rows]
    
    async def get_test_result_by_id(self, result_id: int) -> Optional[TestResult]:
        row = await self.fetch_one("SELECT * FROM test_results WHERE id = $1", result_id)
        return TestResult(**dict(row)) if row else None
        
    async def get_formula_result_by_id(self, result_id: int) -> Optional[FormulaResult]:
        row = await self.fetch_one("SELECT * FROM formula_rsp_results WHERE id = $1", result_id)
        return FormulaResult(**dict(row)) if row else None
