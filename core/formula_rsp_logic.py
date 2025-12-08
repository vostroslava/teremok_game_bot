from dataclasses import dataclass, field
from typing import List, Dict, Optional
from .formula_rsp_types import FORMULA_RSP_TYPES, RSPTypeData, get_rsp_type

@dataclass
class FormulaRSPResult:
    primary_code: str
    primary_name: str
    secondary_codes: List[str]
    scores: Dict[str, int]
    description: str
    recommendations: List[str]
    emoji: str
    result_object: Optional[RSPTypeData] = field(default=None)
    id: Optional[int] = None

def compute_formula_rsp(answers: List[str]) -> FormulaRSPResult:
    """
    Calculate R/S/P result based on answers list.
    answers: list of codes ['result', 'status', 'process', ...]
    """
    scores = {
        "result": 0,
        "status": 0,
        "process": 0
    }
    
    # Count scores
    for ans in answers:
        if isinstance(ans, dict):
            ans = ans.get('value')
            
        if ans in scores:
            scores[ans] += 1
            
    # Find max score
    max_score = -1
    for s in scores.values():
        if s > max_score:
            max_score = s
            
    # Find all types with max score
    leaders = [code for code, s in scores.items() if s == max_score]
    
    # Logic for determining primary type
    # If tie, we can pick the first one from priority or return "mixed"
    # User request: "If equal - mark as mixed and show both OR create a 'Mixed Profile'"
    # Ideally, we return the primary one as the first in leaders list (arbitrary tie-break or specific order)
    # Let's enforce priority: Result > Status > Process if tie? 
    # Or just take the first one found.
    
    primary_code = leaders[0]
    
    # In case of tie, secondary codes will be the others from 'leaders' + others with high scores?
    # Simple logic: Primary is the first leader. Secondary are other leaders.
    
    secondary_codes = [c for c in leaders if c != primary_code]
    
    # If no secondary codes from tie, maybe add the runner-up?
    if not secondary_codes:
        # Find runner-up
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        # sorted_scores[0] is primary
        if len(sorted_scores) > 1 and sorted_scores[1][1] > 0:
            secondary_codes.append(sorted_scores[1][0])
            
    t_data = get_rsp_type(primary_code)
    
    # If it is a perfect tie (e.g. 4-4-4), 'leaders' has 3 items. primary is 'result' (if iteration order).
    # We might want to customize the name if it is mixed?
    # For now, keep it simple as requested: "Primary Type" + "Secondary codes".
    
    return FormulaRSPResult(
        primary_code=t_data.code,
        primary_name=t_data.name,
        secondary_codes=secondary_codes,
        scores=scores,
        description=t_data.short_description,
        recommendations=t_data.recommendations,
        emoji=t_data.emoji,
        result_object=t_data
    )
