from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Dict, Any, List, Union

class TestResult(BaseModel):
    id: Optional[int] = None
    user_id: int
    result_type: str
    scores: Optional[Union[Dict[str, Any], str]] = None
    answers: Optional[Union[Dict[str, Any], str]] = None
    product: str = "teremok"
    created_at: Optional[datetime] = None

class FormulaResult(BaseModel):
    id: Optional[int] = None
    user_id: int
    primary_type_code: str
    primary_type_name: str
    scores: Optional[Union[Dict[str, Any], str]] = None
    answers: Optional[Union[List[Any], str]] = None
    created_at: Optional[datetime] = None
