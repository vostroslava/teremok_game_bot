from dataclasses import dataclass
from typing import List, Dict

@dataclass
class Question:
    id: int
    text: str
    options: List[Dict[str, str]] # [{'text': '...', 'score': {'bird': 1}}, ...]

DIAGNOSTIC_QUESTIONS = [
    Question(
        id=1,
        text="Ваш подход к новым задачам на работе?",
        options=[
            {"text": "Делаю только то, что сказали, чтобы не трогали.", "score": {"bird": 2}},
            {"text": "Сразу спрашиваю: 'А что мне за это доплатят?'", "score": {"hamster": 2}},
            {"text": "Берусь, если это поможет мне выделиться перед шефом или получить связи.", "score": {"fox": 2}},
            {"text": "Интересно разобраться и сделать качественно, даже если сложно.", "score": {"professional": 2}}
        ]
    ),
    Question(
        id=2,
        text="Что для вас идеальный рабочий день?",
        options=[
            {"text": "Когда начальник в командировке и можно уйти пораньше.", "score": {"bird": 1, "hamster": 1}},
            {"text": "Когда удалось заключить выгодную сделку и получить бонус.", "score": {"hamster": 2}},
            {"text": "Когда меня публично похвалили на собрании.", "score": {"fox": 2}},
            {"text": "Когда удалось решить сложную проблему и увидеть результат.", "score": {"professional": 2}}
        ]
    ),
    Question(
        id=3,
        text="Как вы относитесь к ошибкам?",
        options=[
            {"text": "Лучше промолчать, авось не заметят.", "score": {"bird": 1, "rat": 1}},
            {"text": "Виноват не я, это обстоятельства/коллеги.", "score": {"fox": 1, "hamster": 1}},
            {"text": "Признаю, ищу причину и исправляю, чтобы не повторилось.", "score": {"professional": 2}},
            {"text": "Ошибки? У меня их не бывает, это другие ошибаются.", "score": {"bear": 1, "wolf": 1}}
        ]
    ),
    Question(
        id=4,
        text="Ваша реакция на просьбу поработать в выходной (без доплаты)?",
        options=[
            {"text": "Ни за что. Нет денег — нет работы.", "score": {"hamster": 3}},
            {"text": "Если шеф будет и это оценит — выйду.", "score": {"fox": 2}},
            {"text": "Если это критично для проекта — выйду и сделаю.", "score": {"professional": 1, "beta_leader": 1}},
            {"text": "Промолчу, но просто не приду или заболею.", "score": {"bird": 2}}
        ]
    ),
    Question(
        id=5,
        text="Что самое важное в компании для вас?",
        options=[
            {"text": "Чтобы вовремя платили и не трогали.", "score": {"bird": 1, "hamster": 1}},
            {"text": "Возможность карьерного роста и статус.", "score": {"fox": 2}},
            {"text": "Профессиональный коллектив и интересные задачи.", "score": {"professional": 2}},
            {"text": "Максимальный доход при минимальных усилиях.", "score": {"hamster": 2, "rat": 1}}
        ]
    )
]

def calculate_result(scores: Dict[str, int]) -> str:
    # Find key with max value
    if not scores:
        return "bird" # default
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    winner_id = sorted_scores[0][0]
    return winner_id
