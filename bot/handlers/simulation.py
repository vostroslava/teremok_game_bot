from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from bot.resources import SCENES

# ============================================================
#                 ЧАСТЬ 2. СИМУЛЯЦИЯ УПРАВЛЕНИЯ
# ============================================================

def init_sim_state(context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Инициализация состояния симуляции.
    """
    user_data = context.user_data
    user_data["sim"] = {
        "current_scene": 0,
        "money": 100,  # 100 — условная базовая точка
        "engagement": 70,  # стартовая вовлечённость
        "risk": 20,  # стартовый риск выгорания/токсичности
        "decisions": [],  # список принятых решений
    }


def build_scene_text(sim: dict) -> str:
    """
    Текст сцены с текущими показателями.
    """
    idx = sim["current_scene"]
    scene = SCENES[idx]

    money = sim["money"]
    engagement = sim["engagement"]
    risk = sim["risk"]

    return (
        f"{scene['title']}\n\n"
        f"{scene['description']}\n\n"
        f"{scene['question']}\n\n"
        f"📊 Текущие показатели компании:\n"
        f"— Деньги: {money} (100 — базовый уровень)\n"
        f"— Вовлечённость: {engagement}\n"
        f"— Риск выгорания/токсичности: {risk}"
    )


def build_scene_keyboard(scene_index: int) -> InlineKeyboardMarkup:
    """
    Кнопки с вариантами решений для сцены.
    """
    scene = SCENES[scene_index]
    buttons = []
    for i, opt in enumerate(scene["options"]):
        buttons.append(
            [
                InlineKeyboardButton(
                    opt["label"],
                    callback_data=f"SIM:{scene_index}:{i}",
                )
            ]
        )
    return InlineKeyboardMarkup(buttons)


async def send_scene(chat_id: int, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Отправляем текущую сцену симуляции.
    """
    user_data = context.user_data
    sim = user_data.get("sim")
    if not sim:
        return

    idx = sim["current_scene"]
    text = build_scene_text(sim)
    keyboard = build_scene_keyboard(idx)
    await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=keyboard)


def format_sim_summary(user_data: dict) -> str:
    """
    Итог симуляции: финальные показатели + расшифровка.
    """
    sim = user_data.get("sim", {})
    if not sim:
        return "Состояние симуляции не найдено."

    money = sim.get("money", 100)
    engagement = sim.get("engagement", 70)
    risk = sim.get("risk", 20)
    decisions = sim.get("decisions", [])

    lines = ["Итоги симуляции управления командой:\n"]

    # Интерпретация денег
    if money < 80:
        money_text = (
            "Компания недозарабатывает или теряет деньги из-за управленческих решений."
        )
    elif money <= 120:
        money_text = (
            "Финансовый результат в допустимом коридоре: без рывков, но и без провалов."
        )
    else:
        money_text = (
            "Агрессивный рост по деньгам, но важно смотреть, какой ценой это достигается."
        )

    # Интерпретация вовлечённости
    if engagement < 50:
        engagement_text = (
            "Вовлечённость просела: часть людей выгорела или ушла в пассивный саботаж."
        )
    elif engagement <= 80:
        engagement_text = (
            "Вовлечённость неровная: часть команды тянет, часть работает «по инструкции»."
        )
    else:
        engagement_text = (
            "Команда в целом вовлечена и чувствует смысл происходящего."
        )

    # Интерпретация риска
    if risk > 60:
        risk_text = (
            "Риск выгорания и токсичных конфликтов высокий — система держится на отдельных людях."
        )
    elif risk >= 30:
        risk_text = (
            "Риск управляемый, но турбулентность присутствует — важны точные решения по людям."
        )
    else:
        risk_text = (
            "Риск выгорания и токсичности низкий — система относительно устойчива."
        )

    lines.append(f"💰 Деньги: {money} (база 100). {money_text}")
    lines.append(f"🔥 Вовлечённость: {engagement}. {engagement_text}")
    lines.append(f"⚠️ Риск выгорания/токсичности: {risk}. {risk_text}\n")

    lines.append("Принятые решения:")
    for d in decisions:
        lines.append(
            f"\n{d['scene_title']}\n"
            f"— Твой выбор: {d['option_label']}\n"
            f"  Эффект: деньги {d['d_money']:+}, вовлечённость {d['d_engagement']:+}, риск {d['d_risk']:+}.\n"
            f"  Комментарий: {d['comment']}"
        )

    lines.append(
        "\nСмысл симуляции: показать, что ставка только на результат любой ценой усиливает Крыс и Лис, "
        "выжигает Хомяков и ядро, а ставка на ядро и прозрачные правила даёт меньше краткосрочного "
        "выигрыша, но сохраняет систему и деньги в долгую."
    )

    return "\n".join(lines)


async def start_sim(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    init_sim_state(context)
    user_data = context.user_data
    sim = user_data["sim"]

    intro = (
        "Запускаем Часть 2 — симуляцию управления.\n\n"
        "У компании есть три показателя:\n"
        "💰 Деньги (базовый уровень — 100).\n"
        "🔥 Вовлечённость команды.\n"
        "⚠️ Риск выгорания и токсичности.\n\n"
        "Ты примешь несколько ключевых решений, а затем увидишь, "
        "как эти решения бьют по системе и деньгам."
    )
    await query.edit_message_text(intro)
    await send_scene(chat_id=query.message.chat_id, context=context)


async def process_sim_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    data = query.data
    await query.answer()

    try:
        _, scene_idx_str, opt_idx_str = data.split(":", 2)
        scene_idx = int(scene_idx_str)
        opt_idx = int(opt_idx_str)
    except ValueError:
        await query.edit_message_text(
            "Непонятный ответ в симуляции. Нажми /start, чтобы начать заново."
        )
        return

    user_data = context.user_data
    sim = user_data.get("sim")
    if not sim:
        await query.edit_message_text(
            "Сессия симуляции не найдена. Нажми /start, чтобы начать заново."
        )
        return

    # Проверяем, что мы в нужной сцене
    current_scene = sim["current_scene"]
    if scene_idx != current_scene or scene_idx >= len(SCENES):
        await query.edit_message_text(
            "Состояние симуляции сбилось. Нажми /start, чтобы начать заново."
        )
        return

    scene = SCENES[scene_idx]
    if opt_idx < 0 or opt_idx >= len(scene["options"]):
        await query.edit_message_text(
            "Неверный вариант ответа. Нажми /start, чтобы начать заново."
        )
        return

    option = scene["options"][opt_idx]

    # Применяем эффекты
    sim["money"] += option["d_money"]
    sim["engagement"] += option["d_engagement"]
    sim["risk"] += option["d_risk"]

    # Лёгкая нормализация значений (в разумных пределах)
    sim["money"] = max(0, min(sim["money"], 200))
    sim["engagement"] = max(0, min(sim["engagement"], 120))
    sim["risk"] = max(0, min(sim["risk"], 120))

    sim["decisions"].append(
        {
            "scene_id": scene["id"],
            "scene_title": scene["title"],
            "option_label": option["label"],
            "d_money": option["d_money"],
            "d_engagement": option["d_engagement"],
            "d_risk": option["d_risk"],
            "comment": option["comment"],
        }
    )

    # Краткая фиксация выбранного варианта
    feedback = (
        f"Твоё решение:\n{scene['title']}\n— {option['label']}\n\n"
        f"Изменения по показателям: деньги {option['d_money']:+}, "
        f"вовлечённость {option['d_engagement']:+}, риск {option['d_risk']:+}."
    )
    await query.edit_message_text(feedback)

    # Переходим к следующей сцене или завершаем
    sim["current_scene"] += 1
    if sim["current_scene"] < len(SCENES):
        await send_scene(chat_id=query.message.chat_id, context=context)
    else:
        summary_text = format_sim_summary(user_data)
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔁 Сыграть симуляцию ещё раз", callback_data="START_SIM"
                    )
                ]
            ]
        )
        await context.bot.send_message(
            chat_id=query.message.chat_id, text=summary_text, reply_markup=keyboard
        )
