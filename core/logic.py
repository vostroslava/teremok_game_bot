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
    ),
    Question(
        id=6,
        text="Ваше отношение к коллегам?",
        options=[
            {"text": "Каждый сам по себе, зачем мне помогать?", "score": {"bird": 1, "hamster": 1}},
            {"text": "Помогаю, если это выгодно мне или шеф заметит.", "score": {"fox": 2}},
            {"text": "Помогаю, потому что вместе получается лучше.", "score": {"professional": 2}},
            {"text": "Помогаю только 'своим', остальные не важны.", "score": {"wolf": 2}}
        ]
    ),
    Question(
        id=7,
        text="Как вы воспринимаете критику?",
        options=[
            {"text": "Обижаюсь и замыкаюсь в себе.", "score": {"bird": 2}},
            {"text": "Это личная атака, буду мстить.", "score": {"rat": 2, "fox": 1}},
            {"text": "Анализирую и использую для роста.", "score": {"professional": 3}},
            {"text": "Кто они, чтобы меня критиковать?", "score": {"bear": 2}}
        ]
    ),
    Question(
        id=8,
        text="Ваше поведение в конфликте?",
        options=[
            {"text": "Прячусь и жду, пока само рассосётся.", "score": {"bird": 2}},
            {"text": "Ищу, кого обвинить и как извлечь выгоду.", "score": {"rat": 2, "fox": 1}},
            {"text": "Разбираюсь в причинах и предлагаю решение.", "score": {"professional": 3}},
            {"text": "Навожу порядок силой и авторитетом.", "score": {"bear": 1, "wolf": 2}}
        ]
    ),
    Question(
        id=9,
        text="Что вас мотивирует работать лучше?",
        options=[
            {"text": "Страх наказания или увольнения.", "score": {"bird": 3}},
            {"text": "Премии и бонусы.", "score": {"hamster": 3}},
            {"text": "Признание и продвижение по карьере.", "score": {"fox": 3}},
            {"text": "Интерес к задаче и желание сделать хорошо.", "score": {"professional": 3}}
        ]
    ),
    Question(
        id=10,
        text="Ваше отношение к регламентам и правилам?",
        options=[
            {"text": "Соблюдаю, если контролируют.", "score": {"bird": 2}},
            {"text": "Соблюдаю, если это выгодно.", "score": {"hamster": 1, "fox": 1}},
            {"text": "Соблюдаю, потому что это правильно.", "score": {"professional": 2}},
            {"text": "Правила не для меня, я особенный.", "score": {"bear": 3}}
        ]
    )
]

def calculate_result(answers: dict) -> dict:
    """
    Calculate test result from user answers.
    
    Args:
        answers: dict of question_id -> option_index
        
    Returns:
        dict with 'type', 'scores', and detailed info
    """
    # Aggregate scores from answers
    total_scores = {}
    
    for q_id_str, option_idx in answers.items():
        q_id = int(q_id_str) if isinstance(q_id_str, str) else q_id_str
        
        # Find question
        question = None
        for q in DIAGNOSTIC_QUESTIONS:
            if q.id == q_id:
                question = q
                break
        
        if question and 0 <= option_idx < len(question.options):
            option = question.options[option_idx]
            for type_id, score in option.get('score', {}).items():
                total_scores[type_id] = total_scores.get(type_id, 0) + score
    
    # Find winner
    if not total_scores:
        winner_id = "bird"
    else:
        sorted_scores = sorted(total_scores.items(), key=lambda x: x[1], reverse=True)
        winner_id = sorted_scores[0][0]
    
    return {
        "type": winner_id,
        "scores": total_scores
    }

