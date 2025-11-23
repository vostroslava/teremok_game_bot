import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.resources import TYPES, BASE_CHARACTERS

# ============================================================
#                 ЧАСТЬ 1. КВИЗ «КТО ЕСТЬ КТО»
# ============================================================

def init_quiz_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Инициализация состояния квиза для пользователя.
    Перемешиваем сотрудников, обнуляем ответы.
    """
    user_data = context.user_data
    characters = BASE_CHARACTERS.copy()
    random.shuffle(characters)
    user_data["quiz"] = {
        "characters": characters,
        "current_index": 0,
        "total": len(characters),
        "phase": "main",  # 'main' или 'retry'
        "answers_first": {},  # первый заход: id -> {chosen, correct}
        "answers_final": {},  # итоговый ответ (после ретрая)
        "score_first": 0,
        "retry_ids": [],  # индексы персонажей, где в первый раз была ошибка
    }


def build_types_keyboard() -> InlineKeyboardMarkup:
    """
    Кнопки с типажами.
    """
    buttons = [
        [
            InlineKeyboardButton(TYPES["BIRD"]["label"], callback_data="QUIZ:BIRD"),
            InlineKeyboardButton(TYPES["HAMSTER"]["label"], callback_data="QUIZ:HAMSTER"),
            InlineKeyboardButton(TYPES["FOX"]["label"], callback_data="QUIZ:FOX"),
        ],
        [
            InlineKeyboardButton(TYPES["RAT"]["label"], callback_data="QUIZ:RAT"),
            InlineKeyboardButton(TYPES["PRO"]["label"], callback_data="QUIZ:PRO"),
            InlineKeyboardButton(TYPES["BEAR"]["label"], callback_data="QUIZ:BEAR"),
        ],
        [
            InlineKeyboardButton(TYPES["ALPHA"]["label"], callback_data="QUIZ:ALPHA"),
            InlineKeyboardButton(TYPES["BETA"]["label"], callback_data="QUIZ:BETA"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def build_main_question_text(characters, index: int, total: int) -> str:
    """
    Вопрос для основного раунда.
    """
    ch = characters[index]
    return (
        f"Сотрудник {index + 1} из {total}.\n\n"
        f"{ch['name']} — {ch['role']}.\n\n"
        f"{ch['description']}\n\n"
        "Кто это по модели «Теремок»?"
    )


def build_retry_question_text(quiz: dict, retry_index: int) -> str:
    """
    Вопрос для повторного раунда (только по ошибочным кейсам).
    """
    characters = quiz["characters"]
    retry_ids = quiz["retry_ids"]
    char_idx = retry_ids[retry_index]
    ch = characters[char_idx]
    total_retry = len(retry_ids)
    return (
        f"Повторный разбор — кейс {retry_index + 1} из {total_retry}.\n\n"
        f"{ch['name']} — {ch['role']}.\n\n"
        f"{ch['description']}\n\n"
        "Кто это по модели «Теремок»?"
    )


async def send_first_question(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляем первый вопрос основного раунда.
    """
    user_data = context.user_data
    quiz = user_data.get("quiz")
    if not quiz:
        return
    idx = quiz["current_index"]
    total = quiz["total"]
    text = build_main_question_text(quiz["characters"], idx, total)
    keyboard = build_types_keyboard()
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def format_quiz_summary(user_data: dict) -> str:
    """
    Итоговый текст по результатам квиза: первый заход + повторный раунд.
    """
    quiz = user_data.get("quiz", {})
    characters = quiz.get("characters", [])
    answers_first = quiz.get("answers_first", {})
    answers_final = quiz.get("answers_final", {})
    total = len(characters)

    score_first = quiz.get(
        "score_first",
        sum(1 for ch in characters if answers_first.get(ch["id"], {}).get("correct")),
    )
    score_final = sum(
        1 for ch in characters if answers_final.get(ch["id"], {}).get("correct")
    )

    lines = [
        f"Результат с первого раза: {score_first} из {total}.",
        f"Итоговый результат после повторной попытки: {score_final} из {total}.\n",
        "Разбор по сотрудникам:",
    ]

    for ch in characters:
        ch_id = ch["id"]
        name = ch["name"]
        correct_code = ch["correct_type"]
        correct_label = TYPES[correct_code]["label"]
        explanation = ch.get("explanation", "")

        first = answers_first.get(ch_id)
        final = answers_final.get(ch_id, first)

        if first is None:
            first_text = "ответа не было"
        else:
            first_label = TYPES.get(first["chosen"], {"label": "?"})["label"]
            suffix = " (верно)" if first["correct"] else " (неверно)"
            first_text = first_label + suffix

        extra_line = ""
        if final is not None and first is not None and final["chosen"] != first["chosen"]:
            final_label = TYPES.get(final["chosen"], {"label": "?"})["label"]
            suffix = " (верно)" if final["correct"] else " (неверно)"
            extra_line = f"  При повторной попытке: {final_label}{suffix}."

        lines.append(
            f"\n• {name}: первый ответ — {first_text}. Правильный типаж: {correct_label}."
        )
        if extra_line:
            lines.append(extra_line)
        if explanation:
            lines.append(f"  Почему так: {explanation}")

    lines.append(
        "\nЭто была Часть 1 — распознавание типажей в большой команде.\n"
        "Теперь можно перейти к Часть 2 — симуляции управленческих решений: "
        "как выбор лидеров, премий и работы с токсичностью бьёт по деньгам и вовлечённости."
    )

    return "\n".join(lines)


async def start_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    init_quiz_state(context)
    user_data = context.user_data
    quiz = user_data["quiz"]

    lines = ["Начинаем тест (Часть 1).\n", "В компании сейчас такая команда:"]
    for ch in quiz["characters"]:
        lines.append(f"• {ch['name']} — {ch['role']}")
    lines.append(
        "\nСначала ты выберешь типажи для всех. "
        "Потом я вернусь только к тем кейсам, где были ошибки. "
        "Полный разбор увидишь в самом конце."
    )
    text = "\n".join(lines)

    await query.edit_message_text(text)
    await send_first_question(chat_id=query.message.chat_id, context=context)


async def process_quiz_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    await query.answer()

    try:
        _, type_code = data.split(":", 1)
    except ValueError:
        await query.edit_message_text("Непонятный ответ. Нажми /start, чтобы начать заново.")
        return

    user_data = context.user_data
    quiz = user_data.get("quiz")
    if not quiz:
        await query.edit_message_text("Сессия теста не найдена. Нажми /start, чтобы начать заново.")
        return

    characters = quiz["characters"]
    total = quiz["total"]

    # Основной раунд
    if quiz["phase"] == "main":
        idx = quiz["current_index"]
        if idx >= total:
            await query.edit_message_text("Тест уже завершён. Нажми /start, чтобы пройти ещё раз.")
            return

        ch = characters[idx]
        ch_id = ch["id"]
        correct_code = ch["correct_type"]
        is_correct = type_code == correct_code

        quiz["answers_first"][ch_id] = {
            "chosen": type_code,
            "correct": is_correct,
        }
        # Итоговый ответ по умолчанию равен первому, пока не было ретрая
        quiz["answers_final"][ch_id] = {
            "chosen": type_code,
            "correct": is_correct,
        }

        quiz["current_index"] += 1

        if quiz["current_index"] < total:
            # Следующий сотрудник того же раунда
            text = build_main_question_text(characters, quiz["current_index"], total)
            keyboard = build_types_keyboard()
            await query.edit_message_text(text=text, reply_markup=keyboard)
        else:
            # Основной раунд завершён — определяем ошибки
            wrong_indices = [
                i
                for i, c in enumerate(characters)
                if not quiz["answers_first"].get(c["id"], {}).get("correct")
            ]
            score_first = sum(
                1
                for c in characters
                if quiz["answers_first"].get(c["id"], {}).get("correct")
            )
            quiz["score_first"] = score_first

            if wrong_indices:
                # Переходим к повторному раунду по ошибочным
                quiz["phase"] = "retry"
                quiz["retry_ids"] = wrong_indices
                quiz["current_index"] = 0
                n_wrong = len(wrong_indices)
                msg = (
                    f"С первого раза ты верно определил {score_first} из {total} сотрудников.\n"
                    f"Давай ещё раз посмотрим на {n_wrong} самых сложных кейсов."
                )
                await query.edit_message_text(msg)

                # Первый вопрос повторного раунда — отдельным сообщением
                text_retry = build_retry_question_text(quiz, 0)
                keyboard = build_types_keyboard()
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=text_retry,
                    reply_markup=keyboard,
                )
            else:
                # Нет ошибок — сразу даём итоговый разбор
                summary_text = format_quiz_summary(user_data)
                await query.edit_message_text(
                    "Отличный результат — всё с первого раза! Ниже разбор."
                )
                keyboard = InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🔁 Пройти тест ещё раз", callback_data="START_QUIZ"
                            )
                        ]
                    ]
                )
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=summary_text,
                    reply_markup=keyboard,
                )

    # Повторный раунд только по ошибочным
    elif quiz["phase"] == "retry":
        retry_ids = quiz["retry_ids"]
        idx_retry = quiz["current_index"]
        if idx_retry >= len(retry_ids):
            await query.edit_message_text("Повторный раунд уже завершён.")
            return

        char_idx = retry_ids[idx_retry]
        ch = characters[char_idx]
        ch_id = ch["id"]
        correct_code = ch["correct_type"]
        is_correct = type_code == correct_code

        # Перезаписываем итоговый ответ по этому сотруднику
        quiz["answers_final"][ch_id] = {
            "chosen": type_code,
            "correct": is_correct,
        }

        quiz["current_index"] += 1

        if quiz["current_index"] < len(retry_ids):
            # Следующий кейс повторного раунда — обновляем то же сообщение
            text_retry = build_retry_question_text(quiz, quiz["current_index"])
            keyboard = build_types_keyboard()
            await query.edit_message_text(text=text_retry, reply_markup=keyboard)
        else:
            # Повторный раунд завершён — даём финальный разбор
            await query.edit_message_text(
                "Все ответы второй попытки приняты. Ниже — разбор по всей команде."
            )
            summary_text = format_quiz_summary(user_data)
            keyboard = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "🔁 Пройти тест ещё раз", callback_data="START_QUIZ"
                        )
                    ]
                ]
            )
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=summary_text,
                reply_markup=keyboard,
            )
    else:
        await query.edit_message_text(
            "Некорректное состояние теста. Нажми /start, чтобы начать заново."
        )
