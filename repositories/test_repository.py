from .base import BaseRepository
from models.test_result import TestResult, FormulaResult
from typing import Optional, List, Dict
import json
import logging

logger = logging.getLogger(__name__)

class TestRepository(BaseRepository):
    
    async def save_test_result(self, result: TestResult) -> int:
        scores_json = json.dumps(result.scores) if isinstance(result.scores, dict) else result.scores
        answers_json = json.dumps(result.answers) if isinstance(result.answers, dict) else result.answers
        
        cursor = await self.execute(
            """INSERT INTO test_results (user_id, result_type, answers, scores, product)
               VALUES (?, ?, ?, ?, ?)""",
            (result.user_id, result.result_type, answers_json, scores_json, result.product)
        )
        return cursor.lastrowid

    async def save_formula_result(self, result: FormulaResult) -> int:
        scores_json = json.dumps(result.scores) if isinstance(result.scores, dict) else result.scores
        answers_json = json.dumps(result.answers) if isinstance(result.answers, (dict, list)) else result.answers
        
        cursor = await self.execute(
            """INSERT INTO formula_rsp_results 
               (user_id, primary_type_code, primary_type_name, scores, answers)
               VALUES (?, ?, ?, ?, ?)""",
            (result.user_id, result.primary_type_code, result.primary_type_name, scores_json, answers_json)
        )
        return cursor.lastrowid

    async def get_user_results(self, user_id: int) -> List[TestResult]:
        rows = await self.fetch_all(
            "SELECT * FROM test_results WHERE user_id = ? ORDER BY created_at DESC",
            (user_id,)
        )
        return [TestResult(**dict(row)) for row in rows]
    
    async def get_test_result_by_id(self, result_id: int) -> Optional[TestResult]:
        row = await self.fetch_one("SELECT * FROM test_results WHERE id = ?", (result_id,))
        return TestResult(**dict(row)) if row else None
        
    async def get_formula_result_by_id(self, result_id: int) -> Optional[FormulaResult]:
        row = await self.fetch_one("SELECT * FROM formula_rsp_results WHERE id = ?", (result_id,))
        return FormulaResult(**dict(row)) if row else None
