from repositories.test_repository import TestRepository
from models.test_result import TestResult, FormulaResult
from core.logic import calculate_result
from core.formula_rsp_logic import compute_formula_rsp
import logging

logger = logging.getLogger(__name__)

class TestService:
    def __init__(self, test_repo: TestRepository):
        self.test_repo = test_repo

    async def process_teremok_test(self, user_id: int, answers: dict) -> int:
        """Calculate and save Teremok test result"""
        result_data = calculate_result(answers)
        
        result = TestResult(
            user_id=user_id,
            result_type=result_data['type'],
            scores=result_data.get('scores', {}),
            answers=answers,
            product="teremok"
        )
        
        return await self.test_repo.save_test_result(result)

    async def process_formula_rsp(self, user_id: int, answers: list) -> FormulaResult:
        """Calculate and save Formula RSP result"""
        # Calculate
        computed = compute_formula_rsp(answers)
        
        # Create model
        result = FormulaResult(
            user_id=user_id,
            primary_type_code=computed.primary_code,
            primary_type_name=computed.primary_name,
            scores=computed.scores,
            answers=answers
        )
        
        # Save
        result_id = await self.test_repo.save_formula_result(result)
        result.id = result_id
        
        # Return full computer result object for frontend (adding derived fields)
        return computed

    async def get_all_tests_full(self, limit: int = 100, product: str = None,
                                  result_type: str = None, days: int = None,
                                  sort_by: str = "created_at", sort_order: str = "desc") -> list:
        return await self.test_repo.get_all_tests_full(limit, product, result_type, days, sort_by, sort_order)

    async def get_recent_tests_full(self, limit: int = 10) -> list:
        return await self.test_repo.get_recent_tests_full(limit)
