from typing import List, Dict
from dataclasses import dataclass
from .formula_levels import FORMULA_LEVELS, FormulaLevel

@dataclass
class FormulaResult:
    total_score: int
    level: FormulaLevel

@dataclass
class Question:
    id: int
    text: str

FORMULA_QUESTIONS = [
    Question(id=1, text="Этот сотрудник соблюдает договорённости и правила, даже когда за ним никто не следит."),
    Question(id=2, text="Если меняются регламенты или процессы, он сам уточняет детали и достаточно быстро перестраивает свою работу."),
    Question(id=3, text="При принятии решений он опирается на интересы компании, а не только на своё удобство и настроение."),
    Question(id=4, text="Он не ищет обходные пути, чтобы «обойти систему», а старается решать вопросы в рамках общих правил."),
    Question(id=5, text="Его поведение помогает держать порядок и дисциплину в команде: с ним другим проще соблюдать договорённости."),
    Question(id=6, text="Он спокойно относится к контролю, отчётности и планёркам — не воспринимает это как личное недоверие."),
    Question(id=7, text="Если что-то идёт не по плану, он не просто критикует систему, а предлагает конкретные решения."),
    Question(id=8, text="При смене руководителя, задач или формата работы не уходит в саботаж, а ищет, как встроиться в новые правила."),
    Question(id=9, text="Даже когда ему что-то не нравится, он обсуждает это по-взрослому и в конструктиве, а не через пассивный саботаж."),
    Question(id=10, text="Если он берёт на себя ответственность за участок работы, на него действительно можно положиться в долгую.")
]

# Варианты ответов (общие для всех вопросов)
FORMULA_OPTIONS = [
    {"value": 1, "text": "Почти никогда"},
    {"value": 2, "text": "Иногда"},
    {"value": 3, "text": "Часто"},
    {"value": 4, "text": "Практически всегда"}
]

def compute_formula_level(scores: List[int]) -> FormulaResult:
    """
    Calculate Formula level based on scores list (integers 1-4).
    Max score: 40. Min score: 10.
    """
    total_score = sum(scores)
    
    # Interpretation logic
    if total_score >= 34:
        code = "green"
    elif total_score >= 27:
        code = "yellow"
    elif total_score >= 19:
        code = "orange"
    else:
        code = "red"
        
    level = FORMULA_LEVELS.get(code)
    # Fallback just in case
    if not level:
        level = FORMULA_LEVELS["red"]
        
    return FormulaResult(
        total_score=total_score,
        level=level
    )
